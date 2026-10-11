#!/usr/bin/env python3
"""Capture only 3,360 missing Haiku/Llama V3.1-frozen main choices.

An exploratory postcalibration five-model expansion. The finished three-model
archive is immutable. Exact frozen prompts, no model-call retries, aggregate
$8 project budget including all unresolved holds, and raw receipt retention.
"""
from __future__ import annotations
import argparse,collections,concurrent.futures,datetime as dt,hashlib,json,math,os,threading,urllib.error,urllib.request
from pathlib import Path
from v3_1_economic_design import ROOT,build

CONF=ROOT/"config"/"v3_4-five-model-expansion-freeze.json"
DEST=ROOT/"results"/"private"/"v3_4-added-models"
MODELS=("anthropic/claude-haiku-4.5","meta-llama/llama-3.3-70b-instruct")
STOP=threading.Event()
LOCK=threading.RLock()
TOKEN=None
STATE={"known_usd":0.0,"unknown_hold_usd":0.0,"inflight":{},"attempts":0,
       "valid":0,"invalid":0,"stop_reason":None}
API="https://openrouter.ai/api/v1"

def utc():return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def write_json(path,record):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def load_frozen():
    cfg=json.loads(CONF.read_text())
    if cfg["protocol_id"]!="v3.4-five-model-main-expansion-2026-10-11":
        raise RuntimeError("UNRECOGNIZED_FROZEN_STUDY")
    if tuple(cfg["new_models"])!=MODELS or cfg["budget"]["additional_spending_hard_cap_usd"]!=1.70:
        raise RuntimeError("MODELS_OR_BUDGET_CHANGED")
    for name,sha in (
        ("scripts/v3_1_economic_design.py",cfg["frozen_source"]["generator_blob_sha"]),
        ("data/v3_1/context_inventory.jsonl",cfg["frozen_source"]["inventory_blob_sha"])):
        raw=(ROOT/name).read_bytes()
        actual=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if actual!=sha:raise RuntimeError("FROZEN_GENERATOR_OR_CONTEXT_CHANGED")
    scenarios=build("main")
    if len(scenarios)!=1680 or len({s["trial_id"] for s in scenarios})!=1680:
        raise RuntimeError("INVALID_SOURCE_MANIFEST")
    digest=hashlib.sha256("".join(json.dumps(s,ensure_ascii=False,sort_keys=True)+"\n" for s in scenarios).encode()).hexdigest()
    if digest!=cfg["frozen_source"]["full_main_manifest_sha256"]:
        raise RuntimeError("FROZEN_SOURCE_MANIFEST_HASH_FAILED")
    return cfg,scenarios

def old_provenance(cfg):
    # Both existing model results and accounting are retained. Verify the complete
    # per-trial JSONL before making any paid call.
    path=ROOT/"results"/"public"/"v3_3-all-5040-cells.jsonl"
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(rows)!=5040:raise RuntimeError("MISSING_ORIGINAL_THREE_MODEL_DATA")
    count=collections.Counter(x["model"] for x in rows)
    if set(count)!={"openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2"} or any(n!=1680 for n in count.values()):
        raise RuntimeError("OLD_MODEL_INVENTORY_MISMATCH")
    if sum(r["status"]=="VALID" for r in rows)!=4862:
        raise RuntimeError("OLD_VALID_COUNT_MISMATCH")
    if sum(r["status"]=="INVALID" for r in rows)!=178:
        raise RuntimeError("OLD_FAILED_COUNT_MISMATCH")
    return {"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_three_models":dict(count),"valid":4862,"invalid":178}

def budget_limit(cfg):
    b=cfg["budget"]
    names=("prior_known_non_v3_usd","prior_uncertain_hold_usd",
           "v3_1_known_usd","v3_1_uncertain_hold_usd",
           "v3_2_known_usd","v3_3_known_usd","v3_3_uncertain_hold_usd")
    available=b["project_hard_cap_usd"]-sum(b[n] for n in names)
    cap=min(b["additional_spending_hard_cap_usd"],available)
    if cap<1.69 or cap>1.70:raise RuntimeError("EXPERIMENT_CUMULATIVE_CEILING_INCONSISTENT")
    return cap

def snapshot(cfg,status):
    return {"protocol_id":cfg["protocol_id"],"status":status,"attempts":STATE["attempts"],
            "valid":STATE["valid"],"invalid":STATE["invalid"],
            "new_known_usd":round(STATE["known_usd"],9),
            "new_unknown_hold_usd":round(STATE["unknown_hold_usd"],9),
            "inflight_usd":dict(STATE["inflight"]),
            "incremental_cap_usd":budget_limit(cfg),"stop_reason":STATE["stop_reason"],"utc":utc()}

def api(path,body=None):
    if not isinstance(TOKEN,str) or len(TOKEN)<12:raise RuntimeError("MISSING_API_TOKEN")
    headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/json","User-Agent":"llm-priority-audit/v3.4"}
    if body is not None:headers["Content-Type"]="application/json"
    data=json.dumps(body,ensure_ascii=False,separators=(",",":")).encode() if body is not None else None
    req=urllib.request.Request(API+path,method="POST" if body is not None else "GET",
                               data=data,headers=headers)
    with urllib.request.urlopen(req,timeout=85) as h:
        return json.loads(h.read(4_000_000))

def preflight(cfg):
    details=api("/key").get("data")
    if not isinstance(details,dict) or details.get("is_management_key"):
        raise RuntimeError("CANNOT_VERIFY_LIVE_KEY_BALANCE")
    try:
        balance=float(details["limit_remaining"])
        cap=float(details["limit"])
    except (KeyError,ValueError,TypeError):raise RuntimeError("UNKNOWN_PROVIDER_BALANCE")
    if not math.isfinite(balance) or balance<budget_limit(cfg) or not 0<cap<=100:
        raise RuntimeError("INSUFFICIENT_PROVIDER_BALANCE_FOR_AGGREGATE_CEILING")
    raw=api("/models").get("data")
    if not isinstance(raw,list):raise RuntimeError("CATALOG_UNAVAILABLE")
    idx={r.get("id"):r for r in raw if isinstance(r,dict)}
    prices={}
    for m in MODELS:
        if m not in idx:raise RuntimeError("MODEL_NOT_LISTED_"+m)
        vals=idx[m].get("pricing") or {}
        try:
            inp=float(vals["prompt"])*1e6
            out=float(vals["completion"])*1e6
            request=float(vals.get("request",0) or 0)
            internal=float(vals.get("internal_reasoning",0) or 0)*1e6
        except (ValueError,TypeError,KeyError):raise RuntimeError("MODEL_PRICING_UNREADABLE_"+m)
        if not all(math.isfinite(x) and x>=0 for x in (inp,out,request,internal)):
            raise RuntimeError("MODEL_PRICING_INVALID_"+m)
        if inp>1.5 or out>6.0 or request>0.0 or internal>6.0 or inp<=0 or out<=0:
            raise RuntimeError("MODEL_PRICE_SPIKE_"+m)
        prices[m]={"input":inp,"output":out,"internal":internal}
    return {"verified_utc":utc(),"key_remaining":balance,"models":prices}

def payload(model,row,prices):
    p=prices[model]
    return {
        "model":model,
        "messages":[{"role":"system","content":row["system_message"]},
                    {"role":"user","content":row["user_message"]}],
        "max_tokens":96,"temperature":0,
        "provider":{"allow_fallbacks":False,"sort":"price",
                    "max_price":{"prompt":round(p["input"]*1.1,5),
                                 "completion":round(p["output"]*1.1,5)}},
        "usage":{"include":True}}

def parse(model,response,error):
    if error or not isinstance(response,dict) or response.get("error"):
        return None,"TRANSPORT_ERROR"
    if response.get("model")!=model:return None,"WRONG_RETURNED_MODEL"
    cs=response.get("choices") or []
    if not isinstance(cs,list) or not cs or not isinstance(cs[0],dict):
        return None,"NO_RESPONSE_CHOICE"
    first=cs[0]
    if first.get("finish_reason") not in ("stop","end_turn") or first.get("error"):
        return None,"INCOMPLETE_RESPONSE"
    ans=(first.get("message") or {}).get("content")
    if not isinstance(ans,str) or ans.strip() not in ("A","B"):
        return None,"NOT_AN_EXACT_UPPERCASE_LETTER"
    return ans.strip(),None

def reserve(model,row,cfg):
    # Large temporary in-flight coverage. Unlike earlier experiments, DO NOT
    # stop because one successfully billed response exceeded its estimate.
    hold=0.007 if model==MODELS[0] else 0.003
    key=model+"|"+row["trial_id"]
    with LOCK:
        if STOP.is_set():return None
        running=sum(STATE["inflight"].values())
        if STATE["known_usd"]+STATE["unknown_hold_usd"]+running+hold+0.015>budget_limit(cfg):
            STOP.set();STATE["stop_reason"]="AGGREGATE_PRE_SEND_CAP"
            write_json(DEST/"ledger.json",snapshot(cfg,"AGGREGATE_STOP"))
            return None
        if key in STATE["inflight"]:raise RuntimeError("DUPLICATE_MODEL_TRIAL")
        STATE["inflight"][key]=hold
        write_json(DEST/"ledger.json",snapshot(cfg,"COLLECTING"))
    return hold

def collect_one(model,row,prices,cfg):
    hold=reserve(model,row,cfg)
    if hold is None:return None
    request=payload(model,row,prices)
    response=None;error=None;start=utc()
    try:response=api("/chat/completions",request)
    except urllib.error.HTTPError as e:
        try:
            obj=json.loads(e.read(2000))
            issue=obj.get("error")
            message=(issue.get("message") if isinstance(issue,dict) else issue)
            error="HTTP_"+str(e.code)+":"+str(message)[:180]
        except Exception:error="HTTP_"+str(e.code)
    except Exception as e:error="UNKNOWN_NETWORK_"+type(e).__name__
    letter,problem=parse(model,response,error)
    usage=response.get("usage") if isinstance(response,dict) else None
    observed=usage.get("cost") if isinstance(usage,dict) else None
    cost_ok=type(observed) in (int,float) and math.isfinite(observed) and observed>=0
    valid=letter is not None and cost_ok
    record={
        "protocol_id":cfg["protocol_id"],"model":model,
        "trial_id":row["trial_id"],"family_id":row["family_id"],
        "domain":row["domain"],"mechanism":row["mechanism"],
        "cost_level":row["cost_level"],"presentation":row["presentation"],
        "q_label":row["q_label"],"display_order":row["display_order"],
        "request_sha256":row["request_sha256"],"response_letter":letter if valid else None,
        "selected_canonical":("Q" if letter==row["q_label"] else "N") if valid else None,
        "valid":valid,"issue":problem if not valid else None,
        "provider_error":error,"returned_model":response.get("model") if isinstance(response,dict) else None,
        "complete_envelope":response,
        "prompt_messages":request["messages"],
        "sent_parameters":{k:v for k,v in request.items() if k not in ("messages","model")},
        "known_charge_usd":float(observed) if cost_ok else None,
        "unreconciled_new_liability_usd":None if cost_ok else hold,
        "transient_reservation_usd":hold,"started_utc":start,"finished_utc":utc()
    }
    with LOCK:
        STATE["inflight"].pop(model+"|"+row["trial_id"])
        if cost_ok:STATE["known_usd"]+=float(observed)
        else:STATE["unknown_hold_usd"]+=hold
        STATE["attempts"]+=1
        STATE["valid"]+=int(valid)
        STATE["invalid"]+=int(not valid)
        # Fail closed for large-scale systemic 4xx/model incompatibility.
        if STATE["attempts"]<=120 and STATE["invalid"]>=10:
            STOP.set();STATE["stop_reason"]="INITIAL_PROVIDER_OR_FORMAT_FAILURES"
        if STATE["known_usd"]+STATE["unknown_hold_usd"]+sum(STATE["inflight"].values())>=budget_limit(cfg):
            STOP.set();STATE["stop_reason"]="AGGREGATE_AFTER_RESPONSE_CAP"
        with (DEST/"new-two-model-raw.jsonl").open("a",encoding="utf-8") as h:
            h.write(json.dumps(record,sort_keys=True,ensure_ascii=False)+"\n")
            h.flush();os.fsync(h.fileno())
        write_json(DEST/"ledger.json",snapshot(cfg,"COLLECTING"))
    return record

def collect():
    global TOKEN
    cfg,manifest=load_frozen()
    old=old_provenance(cfg)
    if DEST.exists():raise RuntimeError("STOP_ALREADY_HAVE_OUTPUT_NO_AUTO_PAID_RERUN")
    DEST.mkdir(parents=True)
    STATE["started_utc"]=utc()
    write_json(DEST/"earlier-five-model-base.json",old)
    TOKEN=os.environ.get("OPENROUTER_API_KEY","")
    if len(TOKEN)<12:raise RuntimeError("SECRET_MISSING")
    information=preflight(cfg)
    write_json(DEST/"live-price-and-balance.json",information)
    write_json(DEST/"ledger.json",snapshot(cfg,"STARTED"))
    pairs=[(m,r) for r in manifest for m in MODELS]
    assert len(pairs)==3360 and len({(m,r["trial_id"]) for m,r in pairs})==3360
    print(json.dumps({"two_models":MODELS,"new_requests":3360,
        "5_model_final_total":8400,"max_new_usd":budget_limit(cfg),
        "provider_remaining":information["key_remaining"]}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futs=[pool.submit(collect_one,m,row,information["models"],cfg) for m,row in pairs]
        for i,f in enumerate(concurrent.futures.as_completed(futs),1):
            try:f.result()
            except Exception as exc:
                with LOCK:
                    STOP.set();STATE["stop_reason"]="UNHANDLED_"+type(exc).__name__
                    write_json(DEST/"ledger.json",snapshot(cfg,"CRITICAL_STOP"))
                print(json.dumps({"unhandled":type(exc).__name__,"finished_slots":i}),flush=True)
            if i%300==0 or i==len(pairs):
                print(json.dumps({"completed_scheduled":i,"attempted":STATE["attempts"],
                    "valid":STATE["valid"],"known":round(STATE["known_usd"],6),
                    "unknown":round(STATE["unknown_hold_usd"],6),
                    "stopped":STOP.is_set()}),flush=True)
    complete=STATE["attempts"]==3360 and not STOP.is_set()
    write_json(DEST/"ledger.json",snapshot(cfg,"ALL_ATTEMPTED" if complete else "PARTIAL_STOP"))
    write_json(DEST/"collection-result.json",{
        "status":"ALL_ATTEMPTED" if complete else "PARTIAL_STOP",
        "model_count":2,"new_attempts":STATE["attempts"],"valid_new":STATE["valid"],
        "invalid_new":STATE["invalid"],"previous_cells":5040,
        "total_attempts_after_extension":5040+STATE["attempts"],
        "new_known_usd":round(STATE["known_usd"],9),
        "new_unknown_hold_usd":round(STATE["unknown_hold_usd"],9),
        "stop_reason":STATE["stop_reason"],"utc":utc()})
    return 0 if complete else 2

def check():
    cfg,rows=load_frozen()
    old=old_provenance(cfg)
    assert budget_limit(cfg)==1.70 and len(rows)==1680
    assert old["valid"]==4862 and old["invalid"]==178
    sample=next(r for r in rows if r["q_label"]=="B")
    prices={m:{"input":1.0,"output":5.0,"internal":0} for m in MODELS}
    for m in MODELS:
        request=payload(m,sample,prices)
        assert request["max_tokens"]==96 and request["temperature"]==0
        assert parse(m,{"model":m,"choices":[{"finish_reason":"stop","message":{"content":" B "}}]},None)==("B",None)
        assert parse(m,{"model":m,"choices":[{"finish_reason":"stop","message":{"content":"Choice: B"}}]},None)[0] is None
    print(json.dumps({"offline":"PASS","new_models":MODELS,
        "new_calls":3360,"existing_cells":5040,
        "hard_new_usd":budget_limit(cfg),"no_inference":True}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=("check","collect"),required=True)
    if p.parse_args().mode=="check":return check()
    return collect()
if __name__=="__main__":raise SystemExit(main())
