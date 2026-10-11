#!/usr/bin/env python3
"""Full 3-model exploratory 5040-cell study, reusing 1046 existing DeepSeek calls.

Post-calibration exploratory only. This never executes the original blocked
three-model confirmatory protocol. No old calls are duplicated. Every raw
request and provider response, malformed choice, charge and null is preserved.
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
import threading
import urllib.error
import urllib.request
from pathlib import Path

from v3_1_economic_design import ROOT,build
CONFIG=ROOT/"config"/"v3_3-full-three-model-exploratory-freeze.json"
DEST=ROOT/"results"/"private"/"v3_3-three-model-main"
ORIGINAL=ROOT/"results"/"private"/"v3_3-original-deepseek"
SOURCE=ORIGINAL/"all-raw-responses.jsonl"
API="https://openrouter.ai/api/v1"
MODELS=("openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2")
STOP=threading.Event()
LOCK=threading.RLock()
KEY=None
STATE={"known_new_usd":0.0,"unknown_new_hold_usd":0.0,"inflight_usd":{},
       "sent":0,"valid_new":0,"invalid_new":0,"stop_reason":None}

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def frozen():
    f=json.loads(CONFIG.read_text())
    if f["protocol_id"]!="v3.3-three-model-full-main-2026-10-11" or tuple(f["models"])!=MODELS:
        raise RuntimeError("FREEZE_PROTOCOL_MODEL_CHANGED")
    if f["budget"]["original_global_ceiling_usd"]!=8 or f["budget"]["new_spending_ceiling_usd"]!=4:
        raise RuntimeError("FREEZE_BUDGET_CHANGED")
    for path,known in (("scripts/v3_1_economic_design.py",f["manifest"]["generator_blob_sha"]),
                      ("data/v3_1/context_inventory.jsonl",f["manifest"]["inventory_blob_sha"])):
        raw=(ROOT/path).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if blob!=known:raise RuntimeError("FREEZE_SOURCE_CHANGED_"+path)
    rows=build("main")
    if len(rows)!=1680 or len({r["trial_id"] for r in rows})!=1680:
        raise RuntimeError("MAIN_MANIFEST_WRONG_LENGTH")
    manifest="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows).encode()
    if hashlib.sha256(manifest).hexdigest()!=f["manifest"]["main_manifest_sha256"]:
        raise RuntimeError("FREEZE_MAIN_MANIFEST_CHANGED")
    return f,rows

def import_existing(manifest,f):
    expected=f["prior_data_reuse"]
    raw=[json.loads(x) for x in SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]
    ledger=json.loads((ORIGINAL/"ledger.json").read_text())
    if len(raw)!=expected["expected_valid_record_count"] or ledger["attempted"]!=len(raw):
        raise RuntimeError("SOURCE_1046_COUNT_MISMATCH")
    if ledger["status"]!="MAIN_PARTIAL_OR_INVALID" or ledger["invalid"]!=0:
        raise RuntimeError("SOURCE_PROVENANCE_ORIGINAL_INVALID")
    if abs(ledger["known_new_usd"]-expected["expected_known_charges_usd"])>1e-9:
        raise RuntimeError("SOURCE_RECORDED_CHARGES_DIFFER")
    by_id={x["trial_id"]:x for x in manifest}
    used=set()
    for item in raw:
        tid=item["trial_id"]
        if tid in used or tid not in by_id:raise RuntimeError("DUPLICATE_OR_UNKNOWN_SOURCE_TRIAL")
        used.add(tid)
        row=by_id[tid]
        if (item["requested_model"]!=expected["model"] or
            item["returned_model"]!=expected["model"] or
            item["request_sha256"]!=row["request_sha256"] or
            not item["valid"] or item["selected_canonical"] not in ("Q","N") or
            item["selected_label"] not in ("A","B") or
            item["selected_canonical"]!=("Q" if item["selected_label"]==row["q_label"] else "N")):
            raise RuntimeError("SOURCE_REUSED_CHOICE_MISMATCH")
        if item["cost_usd"] is None or item.get("raw_response") is None:
            raise RuntimeError("SOURCE_UNVERIFIED_COST_OR_NO_RAW_ENVELOPE")
    if len(used)!=1046 or abs(sum(x["cost_usd"] for x in raw)-ledger["known_new_usd"])>1e-6:
        raise RuntimeError("SOURCE_LEDGER_AND_RECORD_CHARGES_DO_NOT_AGREE")
    return raw,used,ledger

def available_ceiling(f):
    b=f["budget"]
    previous=sum(b[k] for k in (
        "non_v3_known_prior_usd","non_v3_uncertain_reserve_usd","v3_1_known_usd",
        "v3_1_unresolved_hold_usd","v3_2_known_usd"))
    return min(b["new_spending_ceiling_usd"],b["original_global_ceiling_usd"]-previous)

def snapshot(f,status):
    return {"study":f["protocol_id"],"status":status,
        "frozen_main_total":5040,"historical_valid_reused":1046,
        "new_requests_sent":STATE["sent"],"new_valid":STATE["valid_new"],
        "new_invalid":STATE["invalid_new"],
        "known_new_usd":round(STATE["known_new_usd"],9),
        "unreconciled_new_hold_usd":round(STATE["unknown_new_hold_usd"],9),
        "inflight_usd":dict(STATE["inflight_usd"]),
        "new_spend_ceiling_usd":available_ceiling(f),
        "stop_reason":STATE["stop_reason"],"utc":utc()}

def api(path,payload=None):
    assert isinstance(KEY,str) and len(KEY)>12
    headers={"Authorization":"Bearer "+KEY,"Accept":"application/json",
            "User-Agent":"LLM-Priority-Audit/v3.3"}
    if payload is not None:headers["Content-Type"]="application/json"
    encoded=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode() if payload is not None else None
    request=urllib.request.Request(API+path,headers=headers,data=encoded,
                                   method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(request,timeout=90) as r:
        return json.loads(r.read(3_000_000))

def prices_and_key(f):
    key=api("/key").get("data")
    if not isinstance(key,dict) or key.get("is_management_key"):
        raise RuntimeError("PROVIDER_KEY_NOT_READABLE")
    try:
        account_remaining=float(key["limit_remaining"])
        cap=float(key["limit"])
    except (TypeError,ValueError,KeyError):raise RuntimeError("PROVIDER_REMAINING_UNREADABLE")
    if not all(math.isfinite(x) for x in (cap,account_remaining)) or not 0<cap<=100 or account_remaining<available_ceiling(f):
        raise RuntimeError("PROVIDER_BALANCE_BELOW_STUDY_CAP")
    modeldata=api("/models").get("data")
    if not isinstance(modeldata,list):raise RuntimeError("PROVIDER_CATALOG_UNREADABLE")
    idx={m.get("id"):m for m in modeldata if isinstance(m,dict)}
    out={}
    for model in MODELS:
        if model not in idx:raise RuntimeError("PROVIDER_MODEL_MISSING_"+model)
        raw=idx[model].get("pricing") or {}
        try:
            inp=float(raw["prompt"])*1e6
            outp=float(raw["completion"])*1e6
            reasoning=float(raw.get("internal_reasoning",0) or 0)*1e6
            perrequest=float(raw.get("request",0) or 0)
        except (KeyError,ValueError,TypeError):
            raise RuntimeError("PRICE_UNPARSEABLE_"+model)
        if not all(math.isfinite(z) and z>=0 for z in (inp,outp,reasoning,perrequest)) or inp<=0 or outp<=0 or perrequest>0:
            raise RuntimeError("PRICE_UNKNOWN_OR_UNSAFE_"+model)
        if inp>2 or outp>8 or reasoning>5:
            raise RuntimeError("PRICE_MORE_EXPENSIVE_THAN_BUDGET_PLAN_"+model)
        out[model]={"input_per_m":inp,"output_per_m":outp,
                    "reasoning_per_m":reasoning}
    return {"key_remaining_before_run":account_remaining,"pricing":out,"verified_utc":utc()}

def parameters(trial,model,prices):
    p=prices[model]
    maxout=256 if model==MODELS[1] else 96
    body={"model":model,
          "messages":[{"role":"system","content":trial["system_message"]},
                      {"role":"user","content":trial["user_message"]}],
          "max_tokens":maxout,
          "provider":{"allow_fallbacks":False,"sort":"price",
                      "max_price":{"prompt":round(p["input_per_m"]*1.1,5),
                                   "completion":round(p["output_per_m"]*1.1,5)}},
          "usage":{"include":True}}
    if model==MODELS[1]:
        body["provider"]["require_parameters"]=True
        body["response_format"]={"type":"json_schema","json_schema":{
            "name":"choice","strict":True,
            "schema":{"type":"object","properties":{"choice":{"type":"string","enum":["A","B"]}},
                      "required":["choice"],"additionalProperties":False}}}
    else:
        body["temperature"]=0
        body["reasoning"]={"enabled":False}
    return body

def parse_choice(model,row,response,error):
    if error or not isinstance(response,dict) or response.get("error"):
        return None,"ERROR_OR_TRANSPORT"
    if response.get("model")!=model:return None,"MODEL_MISMATCH"
    choices=response.get("choices") or []
    if not isinstance(choices,list) or not choices or not isinstance(choices[0],dict):
        return None,"NO_CHOICE"
    first=choices[0]
    if first.get("error") or first.get("finish_reason") not in ("stop","end_turn"):
        return None,"TRUNCATED_OR_INCOMPLETE"
    text=(first.get("message") or {}).get("content")
    if not isinstance(text,str):return None,"NON_TEXT"
    if model==MODELS[1]:
        try:
            decoded=json.loads(text)
            text=decoded.get("choice") if isinstance(decoded,dict) and set(decoded)=={"choice"} else None
        except (ValueError,TypeError):return None,"BAD_JSON"
    else:text=text.strip()
    if text not in ("A","B"):return None,"BAD_CHOICE_FORMAT"
    return text,None

def reserve(model,trial,f):
    # Reservation accounts ONLY for concurrently in-flight exposure and unknown
    # post-response liabilities. No stopping on an observed individual charge
    # exceeding its estimate, per explicit user authorization.
    held={MODELS[0]:0.02,MODELS[1]:0.025,MODELS[2]:0.015}[model]
    key=model+"|"+trial["trial_id"]
    with LOCK:
        if STOP.is_set():return None
        running=sum(STATE["inflight_usd"].values())
        if (STATE["known_new_usd"]+STATE["unknown_new_hold_usd"]+running+held+0.05 >
              available_ceiling(f)):
            STOP.set();STATE["stop_reason"]="PRE_SEND_AGGREGATE_BUDGET_REACHED"
            write_json(DEST/"ledger.json",snapshot(f,"HALTED_AGGREGATE"))
            return None
        if key in STATE["inflight_usd"]:raise RuntimeError("DUPLICATE_INFLIGHT")
        STATE["inflight_usd"][key]=held
        write_json(DEST/"ledger.json",snapshot(f,"COLLECTING"))
        return held

def request_one(trial,model,price,f):
    held=reserve(model,trial,f)
    if held is None:return None
    payload=parameters(trial,model,price)
    started=utc()
    response=None;error=None
    try:response=api("/chat/completions",payload)
    except urllib.error.HTTPError as e:
        try:
            detail=json.loads(e.read(2048))
            emsg=detail.get("error",{})
            error="HTTP_"+str(e.code)+":"+str(emsg.get("message",emsg) if isinstance(emsg,dict) else emsg)[:200]
        except Exception:error="HTTP_"+str(e.code)
    except Exception as e:error="UNCERTAIN_"+type(e).__name__
    letter,problem=parse_choice(model,trial,response,error)
    usage=response.get("usage") if isinstance(response,dict) else None
    cost=usage.get("cost") if isinstance(usage,dict) else None
    has_cost=type(cost) in (int,float) and math.isfinite(cost) and cost>=0
    valid=letter is not None and has_cost
    record={
        "protocol_id":f["protocol_id"],"source":"new_v3_3",
        "model_requested":model,"model_returned":response.get("model") if isinstance(response,dict) else None,
        "trial_id":trial["trial_id"],"family_id":trial["family_id"],
        "domain":trial["domain"],"mechanism":trial["mechanism"],
        "cost_level":trial["cost_level"],"presentation":trial["presentation"],
        "display_order":trial["display_order"],"q_label":trial["q_label"],
        "request_sha256":trial["request_sha256"],
        "selected_label":letter if valid else None,
        "selected_canonical":("Q" if letter==trial["q_label"] else "N") if valid else None,
        "valid":valid,"error":error,"validation_problem":problem if not valid else None,
        "raw_response":response,"request_messages":payload["messages"],
        "request_parameters":{k:v for k,v in payload.items() if k not in ("messages","model")},
        "known_charge_usd":cost if has_cost else None,
        "unknown_liability_held_usd":None if has_cost else held,
        "transient_reservation_usd":held,"started_utc":started,"finished_utc":utc()
    }
    with LOCK:
        key=model+"|"+trial["trial_id"]
        STATE["inflight_usd"].pop(key)
        if has_cost:STATE["known_new_usd"]+=float(cost)
        else:STATE["unknown_new_hold_usd"]+=held
        STATE["sent"]+=1
        STATE["valid_new"]+=int(valid)
        STATE["invalid_new"]+=int(not valid)
        if STATE["sent"]<=100 and STATE["invalid_new"]>=8:
            STOP.set();STATE["stop_reason"]="EARLY_ABNORMAL_TRANSPORT_INVALIDITY"
        # Aggregate-only budget guard: no individual response cost tripwire.
        if STATE["known_new_usd"]+STATE["unknown_new_hold_usd"]+sum(STATE["inflight_usd"].values()) > available_ceiling(f):
            STOP.set();STATE["stop_reason"]="AGGREGATE_BUDGET_EXCEEDED"
        with (DEST/"new-responses.jsonl").open("a",encoding="utf-8") as out:
            out.write(json.dumps(record,sort_keys=True,ensure_ascii=False)+"\n")
            out.flush();os.fsync(out.fileno())
        write_json(DEST/"ledger.json",snapshot(f,"COLLECTING"))
    return record

def collect():
    global KEY
    f,manifest=frozen()
    historical,used,oldledger=import_existing(manifest,f)
    tasks=[(row,model) for row in manifest for model in MODELS
           if not(model==MODELS[2] and row["trial_id"] in used)]
    expected=f["remaining_to_buy"]["total"]
    if len(tasks)!=expected or expected!=3994:raise RuntimeError("FAILED_MISSING_TASK_BUILD")
    if DEST.exists():raise RuntimeError("DUPLICATE_STUDY_RUN_FOLDER")
    DEST.mkdir(parents=True)
    # Keep unmodified prior complete envelopes alongside new complete responses.
    (DEST/"source-deepseek-1046.jsonl").write_bytes(SOURCE.read_bytes())
    write_json(DEST/"reuse-evidence.json",{
        "original_run_id":f["prior_data_reuse"]["source_run"],
        "artifact_id":f["prior_data_reuse"]["artifact_id"],
        "reused_n":len(historical),"reused_cost_usd":oldledger["known_new_usd"],
        "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_ledger_status":oldledger["status"],
        "new_tasks":len(tasks)
    })
    KEY=os.environ.get("OPENROUTER_API_KEY","")
    if not isinstance(KEY,str) or len(KEY)<12:raise RuntimeError("MISSING_OPENROUTER_SECRET")
    prices=prices_and_key(f)
    write_json(DEST/"model-prices-preflight.json",prices)
    write_json(DEST/"ledger.json",snapshot(f,"COLLECTION_STARTED"))
    print(json.dumps({"status":"MAIN_STARTED","reused_valid":1046,"remaining":len(tasks),
                      "three_model_total":5040,"new_aggregate_max_usd":available_ceiling(f)}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(request_one,row,model,prices["pricing"],f) for row,model in tasks]
        for i,future in enumerate(concurrent.futures.as_completed(futures),1):
            try:future.result()
            except Exception as exc:
                with LOCK:
                    STOP.set();STATE["stop_reason"]="UNHANDLED_"+type(exc).__name__
                print(json.dumps({"unhandled":type(exc).__name__,"slot":i}),flush=True)
            if i%350==0 or i==len(tasks):
                print(json.dumps({"scheduled":i,"of":len(tasks),
                    "new_attempted":STATE["sent"],"new_valid":STATE["valid_new"],
                    "known_spending_usd":round(STATE["known_new_usd"],6),
                    "unknown_held_usd":round(STATE["unknown_new_hold_usd"],6),
                    "stopped":STOP.is_set()}),flush=True)
    full=(STATE["sent"]==3994 and STATE["valid_new"]==3994 and not STOP.is_set())
    write_json(DEST/"ledger.json",snapshot(f,"COMPLETE_ALL_VALID" if full else "PARTIAL_OR_INVALID"))
    write_json(DEST/"collection-result.json",{
        "protocol_id":f["protocol_id"],"status":"COMPLETE_ALL_VALID" if full else "PARTIAL_OR_INVALID",
        "original_valid_reused":1046,"new_sent":STATE["sent"],
        "new_valid":STATE["valid_new"],"new_invalid":STATE["invalid_new"],
        "expected_3_model_cells":5040,"complete":full,
        "new_known_charges_usd":round(STATE["known_new_usd"],9),
        "new_unreconciled_hold_usd":round(STATE["unknown_new_hold_usd"],9),
        "stop_reason":STATE["stop_reason"],"finished_utc":utc()})
    return 0 if STATE["sent"]==3994 else 2

def check():
    f,manifest=frozen()
    old,used,ledger=import_existing(manifest,f)
    tasks=[(r,m) for r in manifest for m in MODELS if not(m==MODELS[2] and r["trial_id"] in used)]
    assert len(tasks)==3994 and len(used)==1046 and len(tasks)+len(used)==5040
    assert available_ceiling(f)==4.0
    sample=next(x for x in manifest if x["q_label"]=="B")
    p={m:{"input_per_m":1.0,"output_per_m":2.0,"reasoning_per_m":0.0} for m in MODELS}
    g=parameters(sample,MODELS[1],p)
    assert g["response_format"]["json_schema"]["schema"]["properties"]["choice"]["enum"]==["A","B"]
    assert "reasoning" not in g
    assert parse_choice(MODELS[1],sample,{"model":MODELS[1],
        "choices":[{"finish_reason":"stop","message":{"content":'{"choice":"B"}'}}]},None)==("B",None)
    assert parse_choice(MODELS[1],sample,{"model":MODELS[1],
        "choices":[{"finish_reason":"stop","message":{"content":"The answer is B"}}]},None)[0] is None
    assert parse_choice(MODELS[0],sample,{"model":MODELS[0],
        "choices":[{"finish_reason":"stop","message":{"content":"B"}}]},None)==("B",None)
    print(json.dumps({"offline_only":True,"manifest":len(manifest),"imported_valid":len(used),
        "new_to_purchase":len(tasks),"aggregate_max_usd":available_ceiling(f),
        "source_charges_usd":ledger["known_new_usd"]}),flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--mode",choices=("check","collect"),required=True)
    mode=a.parse_args().mode
    return check() if mode=="check" else collect()

if __name__=="__main__":
    raise SystemExit(main())
