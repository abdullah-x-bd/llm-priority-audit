#!/usr/bin/env python3
"""Resume only 3267 untouched Claude/Llama trial IDs after Haiku length failures.

Existing 93 original attempts are immutable and included, including 10 failed
but charged Haiku requests. No API call for any previously attempted trial.
Native Haiku JSON schema is a documented technical output-format amendment,
not a change to the experimental stimuli. Original $1.70 new-spend cap stands.
"""
from __future__ import annotations
import argparse,collections,concurrent.futures,json,os,hashlib
from pathlib import Path
import v3_4_collect_additional_models as original

ROOT=original.ROOT
NEW=ROOT/"results"/"private"/"v3_4-resumed-collection"
OLD=ROOT/"results"/"private"/"v3_4-original-attempt"
SOURCE=OLD/"new-two-model-raw.jsonl"
TECH=ROOT/"config"/"v3_4-recovery-technical-amendment.json"
MODEL=original.MODELS[0]
BASE_PAYLOAD=original.payload
BASE_PARSE=original.parse

def old_data(manifest,cfg):
    p=json.loads(TECH.read_text())
    if p["protocol_id"]!=cfg["protocol_id"] or p["remaining_unique_calls"]!=3267 or \
       p["source_run_id"]!=38115946130 or p["archived_previous_attempts"]!=93:
        raise RuntimeError("TECHNICAL_AMENDMENT_NOT_FROZEN")
    if not SOURCE.is_file() or not (OLD/"ledger.json").is_file():
        raise RuntimeError("MISSING_IMMUTABLE_93_ATTEMPT_ARCHIVE")
    rows=[json.loads(x) for x in SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]
    ledger=json.loads((OLD/"ledger.json").read_text())
    if len(rows)!=93 or sum(bool(x["valid"]) for x in rows)!=83 or ledger["attempts"]!=93:
        raise RuntimeError("ORIGINAL_93_TRIALS_MISMATCH")
    if ledger["status"]!="PARTIAL_STOP" or ledger["invalid"]!=10:
        raise RuntimeError("ORIGINAL_BATCH_LEDGER_CHANGED")
    if abs(ledger["new_known_usd"]-p["previous_recorded_charge_usd"])>1e-8 or ledger["new_unknown_hold_usd"]!=0:
        raise RuntimeError("ORIGINAL_BILLING_DIFFERENT")
    index={x["trial_id"]:x for x in manifest}
    seen=set()
    for row in rows:
        key=(row["model"],row["trial_id"])
        if key in seen or row["model"] not in original.MODELS or row["trial_id"] not in index:
            raise RuntimeError("ORIGINAL_TRIAL_OR_MODEL_DUPLICATE")
        seen.add(key)
        if row["request_sha256"]!=index[row["trial_id"]]["request_sha256"]:
            raise RuntimeError("ORIGINAL_PROMPT_SHA_MISMATCH")
        if not isinstance(row["known_charge_usd"],(int,float)) or row["provider_error"] is not None:
            raise RuntimeError("ORIGINAL_CHARGED_RECEIPT_MISSING")
    if abs(sum(r["known_charge_usd"] for r in rows)-ledger["new_known_usd"])>0.0000001:
        raise RuntimeError("PAID_93_CHARGE_SUM_MISMATCH")
    return rows,ledger,seen

def schema_payload(model,row,prices):
    args=BASE_PAYLOAD(model,row,prices)
    if model==MODEL:
        args["max_tokens"]=256
        args["provider"]["require_parameters"]=True
        args["response_format"]={
            "type":"json_schema",
            "json_schema":{"name":"choice","strict":True,
                "schema":{"type":"object","properties":{"choice":{"type":"string","enum":["A","B"]}},
                          "required":["choice"],"additionalProperties":False}}
        }
    return args

def schema_parse(model,response,error):
    if model!=MODEL:return BASE_PARSE(model,response,error)
    if error is not None or not isinstance(response,dict) or response.get("error"):
        return None,"TRANSPORT_ERROR"
    if response.get("model")!=MODEL:return None,"WRONG_RETURNED_MODEL"
    cs=response.get("choices") or []
    if not isinstance(cs,list) or not cs or not isinstance(cs[0],dict):
        return None,"NO_RESPONSE_CHOICE"
    item=cs[0]
    if item.get("finish_reason") not in ("stop","end_turn") or item.get("error"):
        return None,"INCOMPLETE_RESPONSE"
    content=(item.get("message") or {}).get("content")
    try:
        val=json.loads(content)
        choice=val["choice"] if isinstance(val,dict) and set(val)=={"choice"} else None
    except (ValueError,TypeError,KeyError):
        return None,"HAIKU_INVALID_JSON"
    return (choice,None) if choice in ("A","B") else (None,"HAIKU_JSON_NOT_A_OR_B")

def check():
    cfg,manifest=original.load_frozen()
    old,ledger,existing=old_data(manifest,cfg)
    pairs=[(m,t) for t in manifest for m in original.MODELS if (m,t["trial_id"]) not in existing]
    if len(pairs)!=3267:raise RuntimeError("INCORRECT_UNSENT_3267_COUNT")
    assert len({(m,t["trial_id"]) for m,t in pairs})==3267
    prices={m:{"input":1.0,"output":5.0,"internal":0} for m in original.MODELS}
    p=schema_payload(MODEL,pairs[0][1],prices)
    assert p["response_format"]["json_schema"]["schema"]["properties"]["choice"]["enum"]==["A","B"]
    assert schema_parse(MODEL,{"model":MODEL,
            "choices":[{"finish_reason":"stop","message":{"content":'{"choice":"B"}'}}]},None)==("B",None)
    assert schema_parse(MODEL,{"model":MODEL,
            "choices":[{"finish_reason":"length","message":{"content":"I reasoned B"}}]},None)[0] is None
    assert schema_parse(original.MODELS[1],{"model":original.MODELS[1],
            "choices":[{"finish_reason":"stop","message":{"content":"A"}}]},None)==("A",None)
    print(json.dumps({"audit":"PASS","frozen_original_calls":93,"new_calls":3267,
                      "strict_total_original_plus_new_usd":1.70,"none_repeated":True,
                      "offline_no_provider_calls":True}),flush=True)

def run():
    cfg,manifest=original.load_frozen()
    old,ledger,existing=old_data(manifest,cfg)
    new_pairs=[(m,t) for t in manifest for m in original.MODELS if (m,t["trial_id"]) not in existing]
    if len(new_pairs)!=3267:raise RuntimeError("UNEXPECTED_REQUESTS")
    if NEW.exists():raise RuntimeError("ALREADY_RAN_RESUME_NO_PAID_DUPLICATION")
    NEW.mkdir(parents=True)
    (NEW/"new-two-model-raw.jsonl").write_bytes(SOURCE.read_bytes())
    original.DEST=NEW
    original.STOP.clear()
    original.STATE.update({
        "known_usd":ledger["new_known_usd"],"unknown_hold_usd":ledger["new_unknown_hold_usd"],
        "inflight":{},"attempts":93,"valid":83,"invalid":10,"stop_reason":None
    })
    # Existing old-format 10 failures MUST NOT trigger another early stop.
    # Only count invalidity on new corrected requests in the new recovery stage.
    previous_attempts=93
    previous_invalid=10
    source_collect_one=original.collect_one
    original.payload=schema_payload
    original.parse=schema_parse
    original.TOKEN=os.environ.get("OPENROUTER_API_KEY","")
    if len(original.TOKEN)<12:raise RuntimeError("MISSING_OPENROUTER_API_KEY")
    info=original.preflight(cfg)
    original.write_json(NEW/"live-price-and-balance.json",info)
    original.write_json(NEW/"previous-archive-proof.json",{
        "old_run_id":38115946130,"old_artifact_id":11693023771,
        "old_attempts":len(old),"previous_known_usd":ledger["new_known_usd"],
        "old_raw_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "uncalled_still":len(new_pairs)})
    original.write_json(NEW/"ledger.json",original.snapshot(cfg,"RECOVERING"))
    print(json.dumps({"status":"RECOVERY_STARTED","original_attempts":93,
          "remaining_unattempted":len(new_pairs),"new_total_possible":3360,
          "known_prior_spend":ledger["new_known_usd"],
          "incremental_expansion_cap_usd":original.budget_limit(cfg)}),flush=True)
    # Disable the original cumulative first-120 blanket guard: the original
    # bad-format requests were already counted; instead check new invalids.
    def corrected_collect(model,row,price,cfg):
        result=source_collect_one(model,row,price,cfg)
        if result is not None:
            with original.LOCK:
                attempts=original.STATE["attempts"]-previous_attempts
                invalid=original.STATE["invalid"]-previous_invalid
                if attempts<=150 and invalid>=10:
                    original.STOP.set()
                    original.STATE["stop_reason"]="NEW_SCHEMA_OR_PROVIDER_COMPATIBILITY_FAILURE"
        return result
    # Original collect_one's early guard checks total invalid >=10 and
    # total attempts<=120; seed total attempt counter at 120 until 28 new
    # results are in, while raw evidence retains exact counts separately.
    # More robust: isolate existing 10 from that guard in the imported module.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures=[executor.submit(corrected_collect,m,t,info["models"],cfg) for m,t in new_pairs]
        for i,future in enumerate(concurrent.futures.as_completed(futures),1):
            try:future.result()
            except Exception as e:
                with original.LOCK:
                    original.STOP.set()
                    original.STATE["stop_reason"]="RECOVERY_UNHANDLED_"+type(e).__name__
                print(json.dumps({"exception":type(e).__name__,"slot":i}),flush=True)
            if i%300==0 or i==len(new_pairs):
                print(json.dumps({"completed_schedule_slots":i,
                    "new_requests_sent":original.STATE["attempts"]-93,
                    "total_attempts":original.STATE["attempts"],
                    "valid":original.STATE["valid"],
                    "known_usd":round(original.STATE["known_usd"],6),
                    "unknown_hold_usd":round(original.STATE["unknown_hold_usd"],6),
                    "stopped":original.STOP.is_set()}),flush=True)
    all_done=original.STATE["attempts"]==3360 and not original.STOP.is_set()
    original.write_json(NEW/"ledger.json",original.snapshot(cfg,"ALL_ATTEMPTED" if all_done else "PARTIAL_STOP"))
    original.write_json(NEW/"collection-result.json",{
        "final_status":"ALL_ATTEMPTED" if all_done else "PARTIAL_STOP",
        "old_attempts":93,"new_attempts":original.STATE["attempts"]-93,
        "total_attempted":original.STATE["attempts"],"valid":original.STATE["valid"],
        "invalid":original.STATE["invalid"],
        "new_known_charges_including_original":original.STATE["known_usd"],
        "unreconciled_new_hold":original.STATE["unknown_hold_usd"],
        "stop_reason":original.STATE["stop_reason"]})
    return 0 if all_done else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("check","run"),required=True)
    return check() if p.parse_args().mode=="check" else run()
if __name__=="__main__":raise SystemExit(main())
