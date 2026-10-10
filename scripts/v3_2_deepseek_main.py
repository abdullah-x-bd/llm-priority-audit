#!/usr/bin/env python3
"""Post-calibration exploratory DeepSeek-only full main V3.2.

No pilot/review calls. Manifest and model frozen in an earlier GitHub commit.
Strict incremental $1.50 ceiling. No reruns, no retries, raw envelopes kept.
"""
from __future__ import annotations
import argparse
import collections
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import re
import threading
import urllib.error
import urllib.request
from pathlib import Path

from v3_1_economic_design import ROOT,build

CONFIG=ROOT/"config"/"v3_2-deepseek-exploratory-freeze.json"
DEST=ROOT/"results"/"private"/"v3_2-deepseek-exploratory"
MODEL="deepseek/deepseek-v3.2"
PRICE_PATH="https://openrouter.ai/api/v1"
STOP=threading.Event()
LOCK=threading.RLock()
STATE={"known":0.0,"unknown_hold":0.0,"inflight":{},"attempts":0,"invalid":0,
       "started_utc":None,"stop_reason":None}
KEY=None

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def json_atomic(file,value):
    file.parent.mkdir(parents=True,exist_ok=True)
    tmp=file.with_suffix(file.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmp,file)

def get_config():
    p=json.loads(CONFIG.read_text())
    if p.get("protocol_id")!="v3.2-deepseek-exploratory-2026-10-11" or p["model"]!=MODEL:
        raise RuntimeError("STOP_FROZEN_PROTOCOL_MISMATCH")
    if p["budget"]["strict_new_main_additional_ceiling_usd"]!=1.50:
        raise RuntimeError("STOP_CHANGED_STUDY_BUDGET")
    if p["source_freeze"]["expected_prompts"]!=1680:
        raise RuntimeError("STOP_WRONG_FROZEN_SAMPLE")
    for filename,sha in (
        ("scripts/v3_1_economic_design.py",p["source_freeze"]["generator_git_blob_sha"]),
        ("data/v3_1/context_inventory.jsonl",p["source_freeze"]["inventory_git_blob_sha"]),
    ):
        raw=(ROOT/filename).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if blob!=sha:raise RuntimeError("STOP_SOURCE_FILE_CHANGED_"+filename)
    rows=build("main")
    if len(rows)!=1680 or len({x["trial_id"] for x in rows})!=1680:
        raise RuntimeError("STOP_INCOMPLETE_OR_DUPLICATE_MAIN")
    stream="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows).encode("utf-8")
    if hashlib.sha256(stream).hexdigest()!=p["source_freeze"]["main_manifest_sha256"]:
        raise RuntimeError("STOP_MAIN_DIGEST_MISMATCH")
    if len({x["request_sha256"] for x in rows})!=1680:
        raise RuntimeError("STOP_REUSED_PROMPT")
    return p,rows

def api(path,payload=None):
    if not isinstance(KEY,str) or len(KEY)<12:raise RuntimeError("NO_KEY")
    headers={"Authorization":"Bearer "+KEY,"Accept":"application/json",
             "User-Agent":"LLM-Priority-Audit/V3.2"}
    if payload is not None:headers["Content-Type"]="application/json"
    body=None if payload is None else json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode()
    req=urllib.request.Request(PRICE_PATH+path,headers=headers,
            method="GET" if payload is None else "POST",data=body)
    with urllib.request.urlopen(req,timeout=65) as h:
        return json.loads(h.read(3_000_000))

def price_preflight(p):
    info=api("/key").get("data")
    if not isinstance(info,dict) or info.get("is_management_key"):
        raise RuntimeError("STOP_ACCOUNT_KEY_UNAVAILABLE")
    try:
        remaining=float(info["limit_remaining"])
        account_cap=float(info["limit"])
    except (KeyError,TypeError,ValueError):raise RuntimeError("STOP_UNKNOWN_KEY_BALANCE")
    if not math.isfinite(remaining) or remaining<2.0 or not 0<account_cap<=50:
        raise RuntimeError("STOP_INSUFFICIENT_PROVIDER_KEY_BALANCE_OR_ABNORMAL_KEY_CAP")
    models=api("/models").get("data")
    if not isinstance(models,list):raise RuntimeError("STOP_UNAVAILABLE_MODEL_CATALOGUE")
    match=next((x for x in models if x.get("id")==MODEL),None)
    if match is None:raise RuntimeError("STOP_MODEL_UNLISTED")
    try:
        inp=float(match["pricing"]["prompt"])*1e6
        out=float(match["pricing"]["completion"])*1e6
        reasoning=float(match["pricing"].get("internal_reasoning",0) or 0)*1e6
        per_request=float(match["pricing"].get("request",0) or 0)
    except (TypeError,ValueError,KeyError):raise RuntimeError("STOP_UNVERIFIED_MODEL_PRICE")
    if not all(math.isfinite(a) and a>=0 for a in (inp,out,reasoning,per_request)):
        raise RuntimeError("STOP_INVALID_PRICE")
    if inp<=0 or out<=0 or per_request!=0:
        raise RuntimeError("STOP_UNSUPPORTED_PRICE")
    if inp>1.00 or out>3.00 or reasoning>0.5:
        raise RuntimeError("STOP_UNEXPECTED_PRICE_SPIKE")
    return {"input_per_m":inp,"output_per_m":out,"reasoning_per_m":reasoning,
            "key_remaining_before_run":remaining,"price_catalog_verified_utc":stamp()}

def budget_limit(p):
    b=p["budget"]
    prior=(b["previous_known_non_v3_1_usd"]+b["previous_unknown_reserve_usd"]
           +b["v3_1_known_spending_usd"]+b["v3_1_unknown_hold_usd"])
    return min(b["strict_new_main_additional_ceiling_usd"],
               b["global_project_cap_usd"]-prior)

def estimate_hold(row,price):
    # Allocation is deliberately much higher than planned usage.
    char_count=len(row["system_message"])+len(row["user_message"])
    base=(((char_count+500)*price["input_per_m"]+
           384*(price["output_per_m"]+price["reasoning_per_m"]))/1e6)
    return max(0.001,round(base*2.5+0.0003,8))

def snapshot(p,status):
    return {"protocol_id":p["protocol_id"],"status":status,
            "attempted":STATE["attempts"],"invalid":STATE["invalid"],
            "known_new_usd":round(STATE["known"],9),
            "held_unknown_usd":round(STATE["unknown_hold"],9),
            "inflight_reservations":dict(STATE["inflight"]),
            "strict_new_spend_ceiling_usd":budget_limit(p),
            "stop_reason":STATE["stop_reason"],
            "started_utc":STATE["started_utc"],"updated_utc":stamp()}

def reserve(row,price,p):
    with LOCK:
        if STOP.is_set():return None
        held=estimate_hold(row,price)
        outstanding=sum(STATE["inflight"].values())
        if STATE["known"]+STATE["unknown_hold"]+outstanding+held>budget_limit(p):
            STOP.set();STATE["stop_reason"]="STOP_PRE_SEND_BUDGET"
            json_atomic(DEST/"ledger.json",snapshot(p,"STOP_BUDGET"))
            return None
        trial=row["trial_id"]
        if trial in STATE["inflight"]:
            raise RuntimeError("DUPLICATE_INFLIGHT")
        STATE["inflight"][trial]=held
        json_atomic(DEST/"ledger.json",snapshot(p,"COLLECTING"))
        return held

def parse_choice(row,response,error):
    if error is not None or not isinstance(response,dict):
        return None,"HTTP_OR_TRANSPORT_FAILURE"
    if response.get("error"):return None,"UPSTREAM_ERROR_ENVELOPE"
    if response.get("model")!=MODEL:return None,"MODEL_MISMATCH"
    c=response.get("choices")
    if not isinstance(c,list) or not c or not isinstance(c[0],dict):
        return None,"NO_CHOICES"
    r=c[0]
    if r.get("error") or r.get("finish_reason") in ("error","length"):
        return None,"INCOMPLETE_OR_ERROR"
    v=(r.get("message") or {}).get("content")
    if not isinstance(v,str) or v.strip() not in ("A","B"):
        return None,"INVALID_LETTER"
    return v.strip(),None

def request_one(row,price,p):
    held=reserve(row,price,p)
    if held is None:return None
    payload={
       "model":MODEL,
       "messages":[{"role":"system","content":row["system_message"]},
                   {"role":"user","content":row["user_message"]}],
       "temperature":0,
       "max_tokens":96,
       "reasoning":{"enabled":False},
       "provider":{"allow_fallbacks":False,"sort":"price",
                  "max_price":{"prompt":round(price["input_per_m"]*1.1,5),
                               "completion":round(price["output_per_m"]*1.1,5)}},
       "usage":{"include":True},
    }
    started=stamp();response=None;error=None
    try:
        response=api("/chat/completions",payload)
    except urllib.error.HTTPError as e:
        try:
            env=json.loads(e.read(4096))
            msg=env.get("error") or {}
            reason=msg.get("message","") if isinstance(msg,dict) else str(msg)
            error=f"HTTP_{e.code}:"+str(reason)[:240]
        except Exception:error="HTTP_"+str(e.code)
    except Exception as e:error="UNKNOWN_TRANSPORT_"+type(e).__name__
    letter,issue=parse_choice(row,response,error)
    usage=response.get("usage") if isinstance(response,dict) else None
    cost=usage.get("cost") if isinstance(usage,dict) else None
    cost_known=type(cost) in (int,float) and math.isfinite(cost) and cost>=0
    valid=letter is not None and cost_known
    observed=(float(cost) if cost_known else None)
    record={
      "protocol_id":p["protocol_id"],"trial_id":row["trial_id"],
      "family_id":row["family_id"],"domain":row["domain"],"mechanism":row["mechanism"],
      "cost_level":row["cost_level"],"extra_cost_minutes":row["extra_cost_minutes"],
      "q_label":row["q_label"],"n_label":row["n_label"],
      "display_order":row["display_order"],"presentation":row["presentation"],
      "expected_q_minutes_hundredths":row["expected_q_minutes_hundredths"],
      "expected_n_minutes_hundredths":row["expected_n_minutes_hundredths"],
      "request_sha256":row["request_sha256"],"messages":payload["messages"],
      "provider_request_options":{k:v for k,v in payload.items() if k not in ("messages","model")},
      "requested_model":MODEL,"returned_model":response.get("model") if isinstance(response,dict) else None,
      "raw_response":response,"transport_error":error,"validation_problem":issue if not valid else None,
      "selected_label":letter if valid else None,
      "selected_canonical":"Q" if valid and letter==row["q_label"] else ("N" if valid else None),
      "valid":bool(valid),"cost_usd":observed,"unreconciled_hold_usd":None if cost_known else held,
      "reservation_usd":held,"started_utc":started,"finished_utc":stamp(),
    }
    with LOCK:
        STATE["inflight"].pop(row["trial_id"])
        if cost_known:
            STATE["known"]+=observed
            if observed>held:
                STOP.set();STATE["stop_reason"]="STOP_OBSERVED_BILL_EXCEEDS_RESERVATION"
        else:STATE["unknown_hold"]+=held
        STATE["attempts"]+=1
        STATE["invalid"]+=int(not valid)
        if STATE["invalid"]>=5 and STATE["attempts"]<=100:
            STOP.set();STATE["stop_reason"]="STOP_EARLY_INVALID_RESPONSE_THRESHOLD"
        if STATE["known"]+STATE["unknown_hold"]>budget_limit(p):
            STOP.set();STATE["stop_reason"]="STOP_AFTER_BILL_EXCEEDS_LIMIT"
        with (DEST/"all-raw-responses.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n")
            f.flush();os.fsync(f.fileno())
        json_atomic(DEST/"ledger.json",snapshot(p,"COLLECTING"))
    return record

def run():
    global KEY
    p,rows=get_config()
    if DEST.exists():
        raise RuntimeError("STOP_DUPLICATE_RUN_OUTPUT_EXISTS")
    DEST.mkdir(parents=True)
    STATE["started_utc"]=stamp()
    KEY=os.environ.get("OPENROUTER_API_KEY","")
    if len(KEY)<12:raise RuntimeError("STOP_MODEL_KEY_ABSENT")
    price=price_preflight(p)
    json_atomic(DEST/"live-price-preflight.json",price)
    json_atomic(DEST/"ledger.json",snapshot(p,"STARTED"))
    print(json.dumps({"study":p["protocol_id"],"model":MODEL,"prompt_count":len(rows),
       "max_new_usd":budget_limit(p),"price_per_million":price}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(request_one,row,price,p) for row in rows]
        for i,future in enumerate(concurrent.futures.as_completed(futures),1):
            try:future.result()
            except Exception as exc:
                with LOCK:
                    STOP.set()
                    STATE["stop_reason"]="STOP_CRITICAL_UNHANDLED_"+type(exc).__name__
                    json_atomic(DEST/"ledger.json",snapshot(p,"STOP_CRITICAL"))
                print(json.dumps({"critical":type(exc).__name__,"at":i}),flush=True)
            if i%200==0 or i==len(rows):
                print(json.dumps({"completed_scheduled_slots":i,"attempted":STATE["attempts"],
                   "known_cost":round(STATE["known"],6),
                   "unknown_hold":round(STATE["unknown_hold"],6),
                   "stopped":STOP.is_set()}),flush=True)
    fully=(STATE["attempts"]==1680 and STATE["invalid"]==0 and not STOP.is_set())
    json_atomic(DEST/"ledger.json",snapshot(p,"MAIN_ALL_VALID" if fully else "MAIN_PARTIAL_OR_INVALID"))
    json_atomic(DEST/"collection-result.json",{
        "study":p["protocol_id"],"model":MODEL,"expected_trials":1680,
        "attempted":STATE["attempts"],"valid":STATE["attempts"]-STATE["invalid"],
        "invalid":STATE["invalid"],"complete_all_valid":fully,
        "known_cost":round(STATE["known"],9),"unknown_hold":round(STATE["unknown_hold"],9),
        "stop_reason":STATE["stop_reason"],"finished_utc":stamp()})
    return 0 if STATE["attempts"]==1680 else 2

def check():
    p,rows=get_config()
    assert budget_limit(p)>0.0 and budget_limit(p)<=1.5
    assert len(rows)==1680 and sum(x["presentation"]=="risk_first" for x in rows)==480
    assert len({x["trial_id"] for x in rows})==1680
    for domain in ("continuation","reversibility","verification"):
        assert sum(x["domain"]==domain for x in rows)==560
    sample=next(x for x in rows if x["q_label"]=="B")
    assert parse_choice(sample,{"model":MODEL,"choices":[{"finish_reason":"stop","message":{"content":"B"}}]},None)==("B",None)
    assert parse_choice(sample,{"model":MODEL,"choices":[{"finish_reason":"stop","message":{"content":"I prefer B."}}]},None)[0] is None
    assert parse_choice(sample,{"model":"other","choices":[{"message":{"content":"B"}}]},None)[0] is None
    print(json.dumps({"offline_test":"PASS","call_count":len(rows),
                      "manifest_sha256":p["source_freeze"]["main_manifest_sha256"],
                      "strict_incremental_budget":budget_limit(p),
                      "no_paid_requests":True}),flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--mode",choices=("check","collect"),required=True)
    args=a.parse_args()
    if args.mode=="check":return check()
    return run()

if __name__=="__main__":
    raise SystemExit(main())
