#!/usr/bin/env python3
"""Resume the frozen V3.1 study from its ORIGINAL GitHub calibration artifact.

This is an operational repair, not permission to alter hypotheses or exclude
unfavourable scientific findings. Original attempted records remain immutable.
The original one-shot run must never be retried.
"""
from __future__ import annotations
import argparse
import collections
import concurrent.futures
import hashlib
import json
import math
import os
import re
import sys
import threading
import urllib.error
from pathlib import Path

import v3_1_single_shot_run as base
from v3_1_economic_design import build

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_RUN_ID=38078421238
ORIGINAL_ARTIFACT_NAME="v3_1-paid-calibration-38078421238"
OLD=ROOT/"results"/"private"/"v3_1-original"
OUT=ROOT/"results"/"private"/"v3_1-single-shot"
AMENDMENT=ROOT/"config"/"v3_1-resume-amendment.json"
ORIGINAL_EXPECTED_SHA256=None
MODELS=("openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2")
GEMINI=MODELS[1]

def load_old_records():
    p=OLD/"calibration-responses.jsonl"
    if not p.is_file():raise RuntimeError("ORIGINAL_ARTIFACT_NOT_DOWNLOADED")
    original=[json.loads(s) for s in p.read_text(encoding="utf-8").splitlines() if s.strip()]
    ledger=json.loads((OLD/"spending-ledger.json").read_text())
    if len(original)!=369 or ledger["records_by_stage"]["calibration"]!=369:
        raise RuntimeError("ORIGINAL_RECORD_COUNT_INCORRECT")
    if ledger["status"]!="CALIBRATION_COMPLETE_NO_GO" or abs(ledger["charged_usd"]-0.05565087)>1e-8:
        raise RuntimeError("ORIGINAL_LEDGER_MISMATCH")
    old_shas=[(r["model_requested"],r["trial_id"]) for r in original]
    if len(old_shas)!=len(set(old_shas)):
        raise RuntimeError("ORIGINAL_DUPLICATE_TRIAL_MODEL")
    return original,ledger

def verify_amendment():
    conf=base.verify_freeze(require_auth=True)
    amend=json.loads(AMENDMENT.read_text())
    expected={
       "protocol_id":"v3.1-2026-10-11-single-shot",
       "operation":"RECOVER_NO_DUPLICATE_PAID_CALIBRATION_THEN_CONDITIONAL_MAIN",
       "source_run_id":38078421238,
       "source_artifact_id":11679079551,
       "preserve_all_original_attempts":True,
       "no_repeat_of_valid_paid_responses":True,
       "gemini_invalid_400_resubmission_only_after_compatible_canary":True,
       "scientific_inclusion_and_gates_unchanged":True,
       "new_spend_cap_usd":5.70,
       "no_automatic_relaunch":True,
    }
    if amend!=expected:
        raise RuntimeError("RESUME_AMENDMENT_NOT_EXACTLY_AUTHORIZED")
    return conf

def recover_overspend_response(r,trial):
    """Technical classification repair, never mutate the archived source record.

    Original DeepSeek content B was returned by the expected model and billed;
    the collector had marked it invalid solely because cost exceeded its reserve.
    """
    if not (r["model_requested"]=="deepseek/deepseek-v3.2" and
            r["status"]=="INVALID_OR_UNATTRIBUTABLE" and
            r["transport_error_type"] is None and
            r["provider_charged_usd"] is not None and
            r["provider_charged_usd"]>r["request_reservation_usd"]):
        return None
    raw=r.get("raw_response_envelope") or {}
    if raw.get("model")!=r["model_requested"] or raw.get("error"):
        return None
    ch=raw.get("choices") or []
    if not ch or ch[0].get("finish_reason")!="stop":
        return None
    txt=((ch[0].get("message") or {}).get("content") or "").strip()
    legal={"A","B"} if trial["mode"]=="delegated" else {"A","B","T"}
    if txt not in legal or r["request_sha256"]!=trial["request_sha256"]:
        return None
    a=dict(r)
    a["original_status"]=r["status"]
    a["original_reservation_error"]=True
    a["status"]="VALID"
    a["selected_label"]=txt
    a["selected_semantic_action"]=("Q" if txt==trial["q_label"] else "N") if trial["mode"]=="delegated" else txt
    if trial["mode"]!="delegated":
        a["calibration_is_correct"]=txt==trial["arithmetic_control_correct_answer"]
    return a

def make_registry(original,cal):
    reference={(m,r["trial_id"]):(r,m) for r in cal for m in MODELS}
    registry={}
    for old in original:
        key=(old["model_requested"],old["trial_id"])
        if key not in reference or old["request_sha256"]!=reference[key][0]["request_sha256"]:
            raise RuntimeError("ORIGINAL_REQUEST_HASH_NOT_IN_FROZEN_MANIFEST")
        if old["status"]=="VALID":
            if key in registry:raise RuntimeError("DUPLICATE_SUCCESS")
            registry[key]=dict(old, recovered_from_prior_run=ORIGINAL_RUN_ID)
        else:
            rescued=recover_overspend_response(old,reference[key][0])
            if rescued:
                registry[key]=dict(rescued,recovered_from_prior_run=ORIGINAL_RUN_ID)
    valid_models=collections.Counter(k[0] for k in registry)
    if valid_models!={"openai/gpt-5.4-mini":123,"deepseek/deepseek-v3.2":123}:
        raise RuntimeError("UNEXPECTED_PREVIOUS_VALID_COUNTS_"+str(valid_models))
    return registry,reference

def save_record(rec):
    with base.WRITE_LOCK:
        path=OUT/"calibration-responses.jsonl"
        with path.open("a",encoding="utf-8") as h:
            h.write(json.dumps(rec,sort_keys=True,ensure_ascii=False)+"\n")
            h.flush()
            os.fsync(h.fileno())

def compatible_payload(trial,model,prices,conf):
    p=prices[model]
    messages=[{"role":"system","content":trial["system_message"]},
              {"role":"user","content":trial["user_message"]}]
    if model==GEMINI:
        # Use model-supported constrained JSON to prevent verbose answers.
        letters=["A","B","T"] if trial["mode"]!="delegated" else ["A","B"]
        structured={"type":"json_schema","json_schema":{"name":"choice","strict":True,"schema":{"type":"object","properties":{"choice":{"type":"string","enum":letters}},"required":["choice"],"additionalProperties":False}}}
        return {"model":model,"messages":messages,"max_tokens":256,"response_format":structured,
                "provider":{"allow_fallbacks":False,"sort":"price","require_parameters":True,
                            "max_price":{"prompt":round(p["input_per_m"]*1.1,6),
                                         "completion":round(p["output_per_m"]*1.1,6)}},
                "usage":{"include":True}}
    return {"model":model,"messages":messages,"max_tokens":conf["sampling"]["max_completion_tokens"],
            "temperature":conf["sampling"]["temperature"],
            "reasoning":{"enabled":False},
            "provider":{"allow_fallbacks":False,"sort":"price",
                        "max_price":{"prompt":round(p["input_per_m"]*1.1,6),
                                     "completion":round(p["output_per_m"]*1.1,6)}},
            "usage":{"include":True}}

def extract_choice(trial,model,resp):
    """Read only a strict single-letter action or constrained JSON result."""
    if not isinstance(resp,dict):return None
    choices=resp.get("choices") or []
    if not choices or not isinstance(choices[0],dict):return None
    val=(choices[0].get("message") or {}).get("content")
    if not isinstance(val,str):return None
    if model==GEMINI:
        try:
            obj=json.loads(val)
            val=obj.get("choice") if isinstance(obj,dict) and set(obj)=={"choice"} else None
        except (ValueError,TypeError):
            return None
    else:
        val=val.strip()
    expected={"A","B","T"} if trial["mode"]!="delegated" else {"A","B"}
    return val if val in expected else None


def is_good_response(trial,model,resp):
    if not isinstance(resp,dict) or resp.get("model")!=model or resp.get("error"):
        return False
    ch=resp.get("choices")
    if not isinstance(ch,list) or not ch or not isinstance(ch[0],dict):
        return False
    if ch[0].get("error") or ch[0].get("finish_reason") not in ("stop", "end_turn"):
        return False
    return extract_choice(trial,model,resp) is not None

def request_once(stage,trial,model,prices,conf):
    payload=compatible_payload(trial,model,prices,conf)
    # Gemini's 512-token cap and observed DeepSeek reasoning spikes require
    # higher holds than the original budget heuristic.
    original=base.reserve_amount(trial,prices[model],payload["max_tokens"])
    extra=4 if model=="deepseek/deepseek-v3.2" else 2
    held=max(original*extra,0.00075)
    with base.WRITE_LOCK:
        if base.STOP.is_set():return None
        cost=base.STATE["charged_usd"]+base.STATE["held_unknown_usd"]+sum(base.STATE["inflight"].values())
        hard=min(conf["budget"]["new_v3_1_spending_cap_usd"],
                 conf["budget"]["global_project_cap_usd"]-base.PAST_KNOWN_USD-base.PAST_UNKNOWN_HELD_USD)
        if cost+held>hard:
            base.STOP.set()
            return None
        key=model+"|"+trial["trial_id"]
        if key in base.STATE["inflight"]:
            raise RuntimeError("DUPLICATE_INFLIGHT_TRIAL")
        base.STATE["inflight"][key]=held
        base.save_ledger("RESUME_RESERVED_"+stage.upper())
    response=None;err=None
    try:
        response=base.http_api("/chat/completions",payload)
    except urllib.error.HTTPError as e:
        try:
            item=json.loads(e.read(2048))
            error=item.get("error")
            if isinstance(error,dict):
                error=error.get("message","")
            err="HTTP_"+str(e.code)+"_"+str(error)[:240]
        except Exception:
            err="HTTP_"+str(e.code)
    except Exception as e:
        err="UNCERTAIN_"+type(e).__name__
    usage=(response.get("usage") or {}) if isinstance(response,dict) else {}
    observed=usage.get("cost")
    known=(type(observed) in (int,float) and math.isfinite(observed) and observed>=0)
    # Do not erase a valid response because of an under-reservation.
    valid=known and is_good_response(trial,model,response)
    raw=(((response.get("choices") or [{}])[0].get("message") or {}).get("content")
         if isinstance(response,dict) and response.get("choices") else None)
    answer=extract_choice(trial,model,response)
    sem=("Q" if answer==trial["q_label"] else "N") if valid and trial["mode"]=="delegated" else answer if valid else None
    rec={
        "stage":stage,"model_requested":model,"model_returned":response.get("model") if isinstance(response,dict) else None,
        "trial_id":trial["trial_id"],"family_id":trial["family_id"],
        "domain":trial["domain"],"mechanism":trial["mechanism"],"mode":trial["mode"],
        "cost_level":trial["cost_level"],"presentation":trial["presentation"],
        "display_order":trial["display_order"],"q_label":trial["q_label"],"n_label":trial["n_label"],
        "request_sha256":trial["request_sha256"],"selected_label":answer if valid else None,
        "selected_semantic_action":sem,"status":"VALID" if valid else "INVALID_OR_UNATTRIBUTABLE",
        "arithmetic_correct_answer":trial["arithmetic_control_correct_answer"] if trial["mode"]!="delegated" else None,
        "calibration_is_correct":answer==trial["arithmetic_control_correct_answer"] if valid and trial["mode"]!="delegated" else None,
        "transport_error_type":err,"raw_response_envelope":response,
        "request_messages":payload["messages"],
        "request_params":{k:v for k,v in payload.items() if k not in ("messages","model")},
        "provider_charged_usd":observed if known else None,
        "conservative_unknown_charge_hold_usd":None if known else held,
        "request_reservation_usd":held,
        "operational_amendment":"NO_RETRY_VALID_ORIGINALS_GEMINI_400_COMPATIBILITY_FIX",
    }
    with base.WRITE_LOCK:
        base.STATE["inflight"].pop(key)
        if known:
            base.STATE["charged_usd"]+=observed
            if observed>held:base.STOP.set()
        else:
            base.STATE["held_unknown_usd"]+=held
        base.STATE["records_by_stage"][stage]+=1
        fn=OUT/(stage+"-resumed-attempts.jsonl")
        with fn.open("a",encoding="utf-8") as h:
            h.write(json.dumps(rec,sort_keys=True,ensure_ascii=False)+"\n")
            h.flush();os.fsync(h.fileno())
        base.save_ledger("RESUME_COLLECTING_"+stage.upper())
    return rec

def canary(conf,prices,cal,registry):
    gem=next((r for r in cal if (GEMINI,r["trial_id"]) not in registry),None)
    if gem is None:raise RuntimeError("NO_GEMINI_CANARY")
    r=request_once("calibration",gem,GEMINI,prices,conf)
    report={"trial_id":gem["trial_id"],
            "valid":r is not None and r["status"]=="VALID",
            "error":r.get("transport_error_type") if r else "NO_ATTEMPT"}
    base.jsonwrite(OUT/"gemini-compatibility-canary.json",report)
    if not report["valid"]:
        raise RuntimeError("GEMINI_CANARY_FAILED_NO_MASS_RETRY")
    return r

def execute():
    conf=verify_amendment()
    original,oldledger=load_old_records()
    cal=build("calibration")
    registry,reference=make_registry(original,cal)
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError("RECOVERY_OUTPUT_ALREADY_EXISTS_NO_AUTO_RELAUNCH")
    OUT.mkdir(parents=True)
    # Account for the first recovery canary independently. That call was charged
    # but was not one of the valid reusable answers. Keep it in the audit.
    prior_canary_path=ROOT/"results"/"private"/"v3_1-failed-canary"/"v3_1-single-shot"/"calibration-resumed-attempts.jsonl"
    if not prior_canary_path.is_file():
        raise RuntimeError("MISSING_PREVIOUS_PAID_CANARY_ARCHIVE")
    prior_canary=[json.loads(x) for x in prior_canary_path.read_text().splitlines() if x.strip()]
    if len(prior_canary)!=1 or prior_canary[0]["model_requested"]!=GEMINI:
        raise RuntimeError("PREVIOUS_CANARY_PROVENANCE_INCONSISTENT")
    prior_charge=prior_canary[0].get("provider_charged_usd")
    if not isinstance(prior_charge,(int,float)) or not (0<=prior_charge<0.01):
        raise RuntimeError("PREVIOUS_CANARY_BILLING_NOT_RECONCILED")
    # Original ledger includes all 123 Gemini errors as UNCERTAIN charges;
    # conservatively KEEP the original unknown $0.22472 hold in budget ceilings.
    base.STATE.update({
        "charged_usd":oldledger["charged_usd"]+prior_charge,
        "held_unknown_usd":oldledger["held_unknown_usd"],
        "inflight":{},
        "records_by_stage":{"calibration":oldledger["records_by_stage"]["calibration"],"main":0}
    })
    base.SECRET=os.environ.get("OPENROUTER_API_KEY","")
    if len(base.SECRET)<12:raise RuntimeError("STOP_API_SECRET_ABSENT")
    prices=base.model_prices(conf["model_roster"])
    remaining=base.key_remaining()
    if remaining<1.0:raise RuntimeError("STOP_KEY_AVAILABLE_TOO_LOW")
    base.save_ledger("RECOVERY_ORIGINAL_IMPORTED")
    # Retain every historical attempt, including Gemini 400 errors; copy explicitly.
    (OUT/"original-calibration-responses.jsonl").write_bytes(
        (OLD/"calibration-responses.jsonl").read_bytes())
    (OUT/"previous-failed-canary.jsonl").write_bytes(prior_canary_path.read_bytes())
    # All salvaged records are re-evaluated under IDENTICAL original stimuli.
    for k in registry:
        save_record(registry[k])
    # First compatibility canary, exactly one. If rejected, STOP and archive.
    try:
        candidate=canary(conf,prices,cal,registry)
    except Exception:
        base.save_ledger("GEMINI_CANARY_STOP")
        raise
    registry[(GEMINI,candidate["trial_id"])]=candidate
    save_record(candidate)
    pairs=[(trial,m) for trial in cal for m in MODELS if (m,trial["trial_id"]) not in registry]
    if len(pairs)!=617: # 864 - 246 recovered - 1 successful Gemini canary
        raise RuntimeError("UNEXPECTED_MISSING_COUNT_"+str(len(pairs)))
    print(json.dumps({"stage":"calibration","original_attempts":369,
                      "valid_original_recovered":246,
                      "gemini_canary_valid":True,
                      "unsent_or_failed_to_collect":len(pairs)}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(request_once,"calibration",r,m,prices,conf) for r,m in pairs]
        for i,fut in enumerate(concurrent.futures.as_completed(futures),1):
            try:r=fut.result()
            except Exception as exc:
                base.STOP.set()
                print(json.dumps({"unhandled_type":type(exc).__name__,"at":i}),flush=True)
                continue
            if r is not None:
                save_record(r)
            if i%125==0:print(json.dumps({"stage":"calibration",
                "completed_schedule_slots":i,"queued":len(pairs),
                "stopped":base.STOP.is_set(),
                "known_new_usd":base.STATE["charged_usd"],
                "unknown_held_usd":base.STATE["held_unknown_usd"]}),flush=True)
    allcal=[json.loads(x) for x in (OUT/"calibration-responses.jsonl").read_text().splitlines() if x]
    unique={(r["model_requested"],r["trial_id"]) for r in allcal}
    if len(unique)!=len(allcal):raise RuntimeError("DUPLICATE_RECOVERED_CALIBRATION")
    passed,gates=base.evaluate_calibration(allcal,conf)
    pre=(False,{"reason":"CALIBRATION_DID_NOT_PASS"})
    if passed and not base.STOP.is_set():
        pre=base.budget_preflight_for_main(allcal,prices,build("main"),conf)
    passed=passed and pre[0] and not base.STOP.is_set()
    report={"stage":"calibration","resume_original_run_id":ORIGINAL_RUN_ID,
            "original_attempts_preserved":369,"valid_original_reused":246,
            "attempted_unique_evaluated":len(allcal),
            "passed_all_gates":passed,"calibration_gates":gates,
            "main_cost_preflight":pre[1],
            "known_charges_usd":base.STATE["charged_usd"],
            "held_unknown_usd":base.STATE["held_unknown_usd"],
            "protocol_id":conf["protocol_id"]}
    base.jsonwrite(OUT/"calibration-report.json",report)
    base.save_ledger("CALIBRATION_COMPLETE_GATE_PASS" if passed else "CALIBRATION_COMPLETE_NO_GO")
    print(json.dumps({"completed_calibration":len(allcal),
                      "gate_pass":passed,"gates":gates,"budget_preflight":pre[1]},sort_keys=True),flush=True)
    print("AUTO_MAIN_GO="+str(passed).lower(),flush=True)
    with open(os.environ.get("GITHUB_OUTPUT","/tmp/v3_1_resume_go.txt"),"a") as h:
        h.write("go="+("true" if passed else "false")+"\n")
    return 0

def execute_main():
    conf=verify_amendment()
    if not (OUT/"calibration-report.json").exists():
        raise RuntimeError("MAIN_BLOCKED_NO_RESUMED_CALIBRATION")
    cal=json.loads((OUT/"calibration-report.json").read_text())
    if not cal.get("passed_all_gates") or not cal.get("main_cost_preflight",{}).get("preflight_passed"):
        raise RuntimeError("MAIN_BLOCKED_CALIBRATION_GATE_FAIL")
    if (OUT/"main-report.json").exists() or (OUT/"main-resumed-attempts.jsonl").exists():
        raise RuntimeError("MAIN_ALREADY_ATTEMPTED_NO_AUTO_RETRY")
    oldledger=json.loads((OUT/"spending-ledger.json").read_text())
    if oldledger.get("status")!="CALIBRATION_COMPLETE_GATE_PASS":
        raise RuntimeError("MAIN_BLOCKED_LEDGER_NOT_GATE_PASS")
    if oldledger.get("inflight"):
        raise RuntimeError("MAIN_BLOCKED_UNRECONCILED_INFLIGHT")
    base.STATE.update({"charged_usd":oldledger["charged_usd"],
                       "held_unknown_usd":oldledger["held_unknown_usd"],
                       "inflight":{}, "records_by_stage":oldledger["records_by_stage"]})
    base.SECRET=os.environ.get("OPENROUTER_API_KEY","")
    if len(base.SECRET)<12:raise RuntimeError("MAIN_KEY_MISSING")
    prices=base.model_prices(conf["model_roster"])
    if base.key_remaining()<0.5:
        raise RuntimeError("MAIN_KEY_BALANCE_LOW")
    # Never silently remove model, task, layout, or cost level after calibration.
    manifest=build("main")
    plan=[(r,m) for r in manifest for m in MODELS]
    assert len(plan)==5040
    base.save_ledger("MAIN_STARTED")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(request_once,"main",r,m,prices,conf) for r,m in plan]
        for i,future in enumerate(concurrent.futures.as_completed(futures),1):
            try:rec=future.result()
            except Exception as exc:
                base.STOP.set()
                print(json.dumps({"critical_type":type(exc).__name__,"main_finished_slots":i}),flush=True)
            if i%300==0 or i==len(plan):
                print(json.dumps({"stage":"main","finished_schedule_slots":i,
                      "known_usd":round(base.STATE["charged_usd"],6),
                      "uncertain_hold_usd":round(base.STATE["held_unknown_usd"],6),
                      "stopped":base.STOP.is_set()}),flush=True)
    rows=[json.loads(x) for x in (OUT/"main-resumed-attempts.jsonl").read_text().splitlines()] \
        if (OUT/"main-resumed-attempts.jsonl").exists() else []
    keys=[(x["model_requested"],x["trial_id"]) for x in rows]
    if len(keys)!=len(set(keys)):
        raise RuntimeError("DUPLICATE_MAIN_TRIAL_MODEL")
    # Record all responses; no data-dependent exclusion in computed outcomes.
    (OUT/"main-responses.jsonl").write_bytes((OUT/"main-resumed-attempts.jsonl").read_bytes()) \
        if rows else None
    completed=(len(rows)==5040 and not base.STOP.is_set())
    analysis=base.summarize_main(rows,conf)
    base.jsonwrite(OUT/"main-report.json",{
        "stage":"main","protocol_id":conf["protocol_id"],
        "status":"COMPLETE" if completed else "PARTIAL_STOP",
        "details":analysis,"captured_requests":len(rows),
        "known_charges_total_usd":base.STATE["charged_usd"],
        "held_unknown_usd":base.STATE["held_unknown_usd"],
        "calibration_gates_unchanged":True,
    })
    base.save_ledger("MAIN_COMPLETE" if completed else "MAIN_PARTIAL_STOP")
    return 0 if completed else 2


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("audit","resume_calibration","resume_main"),required=True)
    args=ap.parse_args()
    if args.mode=="audit":
        conf=base.verify_freeze(require_auth=False)
        original,ledger=load_old_records()
        registry,_=make_registry(original,build("calibration"))
        print(json.dumps({"original_attempts":len(original),"valid_reused":len(registry),
             "old_known_charges_usd":ledger["charged_usd"],
             "old_uncertain_held_usd":ledger["held_unknown_usd"],
             "no_api_calls":True},sort_keys=True))
        return 0
    if args.mode=="resume_calibration":
        execute()
        return 0
    return execute_main()

if __name__=="__main__":
    raise SystemExit(main())
