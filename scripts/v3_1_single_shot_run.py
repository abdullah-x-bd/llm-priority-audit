#!/usr/bin/env python3
"""Frozen V3.1 one-shot OpenRouter calibration then conditional main.

Only run with a separately committed, exact authorization config from GitHub Actions.
Never retries requests, never chooses a new model after seeing results, and records
invalid, failed and missing outputs without recoding them to N.
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
import statistics
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

from v3_1_economic_design import ROOT, build
from v3_1_final_readiness import PAST_KNOWN_USD,PAST_UNKNOWN_HELD_USD

PROTOCOL=ROOT/"config"/"v3_1-frozen-protocol.json"
AUTH=ROOT/"config"/"v3_1-one-shot-authorization.json"
OUT=ROOT/"results"/"private"/"v3_1-single-shot"
CATALOG_URL="https://openrouter.ai/api/v1"
REQUIRED_AUTH={
    "protocol_id":"v3.1-2026-10-11-single-shot",
    "launch":"ONE_SHOT_CALIBRATION_THEN_CONDITIONAL_MAIN",
    "maximum_paid_calibration_requests":864,
    "maximum_paid_main_requests":5040,
    "do_not_rerun_on_failure":True,
}
GIT_BLOBS={
    "scripts/v3_1_economic_design.py":"2e19da975c26386e0d0254aca54681c1bfcefe19",
    "data/v3_1/context_inventory.jsonl":"4d4333a277f1400d721b830a154060d32effd1e2",
}
WRITE_LOCK=threading.RLock()
STOP=threading.Event()
STATE={"charged_usd":0.0,"held_unknown_usd":0.0,"inflight":{},"records_by_stage":{}}
SECRET=""

def time_utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def jsonwrite(path:Path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(temp,path)

def http_api(path:str,body=None):
    assert SECRET and len(SECRET)>12
    headers={"Authorization":"Bearer "+SECRET,"Accept":"application/json",
             "User-Agent":"LLM-Priority-Audit/V3.1-single-shot"}
    if body is not None: headers["Content-Type"]="application/json"
    data=json.dumps(body,separators=(",",":"),ensure_ascii=False).encode() if body is not None else None
    req=urllib.request.Request(CATALOG_URL+path,headers=headers,data=data,
                               method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req,timeout=75) as r:
        return json.loads(r.read(3_000_000))

def model_prices(models):
    catalog=http_api("/models").get("data")
    if not isinstance(catalog,list):raise RuntimeError("STOP_MODEL_CATALOG_MISSING")
    by={p.get("id"):p for p in catalog if isinstance(p,dict)}
    out={}
    for model in models:
        if model not in by:raise RuntimeError("STOP_MODEL_NOT_LISTED_"+model)
        p=by[model].get("pricing") or {}
        try:
            a=float(p["prompt"])*1e6
            b=float(p["completion"])*1e6
            req=float(p.get("request",0) or 0)
            reasoning=float(p.get("internal_reasoning",0) or 0)*1e6
        except (ValueError,TypeError,KeyError):
            raise RuntimeError("STOP_INVALID_CATALOG_PRICES_"+model)
        if not all(math.isfinite(x) and x>=0 for x in (a,b,req,reasoning)):
            raise RuntimeError("STOP_INVALID_PRICE_VALUES_"+model)
        if a<=0 or b<=0 or req>0:
            raise RuntimeError("STOP_UNSUPPORTED_BILLING_"+model)
        out[model]={"input_per_m":a,"output_per_m":b,
                    "internal_reasoning_per_m":reasoning}
    return out

def key_remaining():
    key=http_api("/key").get("data")
    if not isinstance(key,dict) or key.get("is_management_key"):raise RuntimeError("STOP_INVALID_KEY")
    cap=key.get("limit")
    remain=key.get("limit_remaining")
    try:cap,remain=float(cap),float(remain)
    except (ValueError,TypeError):raise RuntimeError("STOP_KEY_CEILING_UNREADABLE")
    if not all(math.isfinite(x) for x in (cap,remain)) or cap<=0 or cap>50.001 or remain<0:
        raise RuntimeError("STOP_KEY_BALANCE_OR_CEILING")
    return remain

def verify_freeze():
    conf=json.loads(PROTOCOL.read_text())
    launch=json.loads(AUTH.read_text())
    if launch!=REQUIRED_AUTH:
        raise RuntimeError("STOP_NOT_AUTHORIZED_OR_AUTH_MODIFIED")
    if conf["protocol_id"]!=REQUIRED_AUTH["protocol_id"] or conf["status"]!="FROZEN_BEFORE_ANY_V3_1_BEHAVIORAL_API_REQUEST":
        raise RuntimeError("STOP_PROTOCOL_CHANGED")
    for filename,blob in GIT_BLOBS.items():
        data=(ROOT/filename).read_bytes()
        got=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        if got!=blob or got!=conf["source_revision"]["script_git_blob_sha" if "script" in filename else "inventory_git_blob_sha"]:
            raise RuntimeError("STOP_STIMULUS_SOURCE_CHANGED_"+filename)
    for stage in ("main","calibration"):
        data=build(stage)
        if len(data)!=({"main":1680,"calibration":288}[stage]):
            raise RuntimeError("STOP_MANIFEST_WRONG_SIZE")
        blob="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in data).encode("utf-8")
        h=sha(blob)
        if h!=conf["source_revision"][stage+"_manifest_sha256"]:
            raise RuntimeError("STOP_MANIFEST_DIGEST_CHANGED_"+stage)
    if conf["budget"]["new_v3_1_spending_cap_usd"]>5.70 or conf["budget"]["global_project_cap_usd"]!=8:
        raise RuntimeError("STOP_BUDGET_CEILING_CHANGED")
    if conf["model_roster"]!=["openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2"]:
        raise RuntimeError("STOP_FROZEN_MODEL_ROSTER_CHANGED")
    return conf

def reserve_amount(trial,price,max_tokens):
    chars=len(trial["system_message"])+len(trial["user_message"])
    # Conservatively allocate one input token per UTF-8 character plus 500
    # and max output/reasoning tokens, plus a price cushion.
    n_in=chars+500
    cost=(n_in*price["input_per_m"]+
          max_tokens*(price["output_per_m"]+price["internal_reasoning_per_m"]))/1e6
    return max(0.0002,round(cost*1.5+0.0001,8))

def start_state(stage):
    OUT.mkdir(parents=True,exist_ok=True)
    ledger=OUT/"spending-ledger.json"
    if stage=="calibration":
        if ledger.exists() or (OUT/"calibration-report.json").exists():
            raise RuntimeError("STOP_DUPLICATE_CALIBRATION_EXECUTION")
        STATE.update({"charged_usd":0.0,"held_unknown_usd":0.0,
                      "inflight":{},"records_by_stage":{"calibration":0,"main":0}})
    else:
        if not ledger.exists():raise RuntimeError("STOP_NO_CALIBRATION_LEDGER")
        record=json.loads(ledger.read_text())
        if record.get("status")!="CALIBRATION_COMPLETE_GATE_PASS" or
           (OUT/"main-report.json").exists():
            raise RuntimeError("STOP_MAIN_NOT_AUTHORIZED_BY_PASSED_CALIBRATION")
        for k in ("charged_usd","held_unknown_usd","records_by_stage"):
            STATE[k]=record[k]
        STATE["inflight"]={}
    save_ledger("STAGE_START_"+stage.upper())

def save_ledger(status):
    ledger={
        "protocol_id":REQUIRED_AUTH["protocol_id"],"status":status,
        "charged_usd":round(STATE["charged_usd"],9),
        "held_unknown_usd":round(STATE["held_unknown_usd"],9),
        "inflight":STATE["inflight"],
        "records_by_stage":STATE["records_by_stage"],
        "timestamp":time_utc(),
    }
    jsonwrite(OUT/"spending-ledger.json",ledger)

def book_reservation(stage,trial,model,prices,conf):
    with WRITE_LOCK:
        if STOP.is_set():return None
        estimate=reserve_amount(trial,prices[model],conf["sampling"]["max_completion_tokens"])
        current=STATE["charged_usd"]+STATE["held_unknown_usd"]+sum(STATE["inflight"].values())
        limit=conf["budget"]["new_v3_1_spending_cap_usd"]
        max_total=conf["budget"]["global_project_cap_usd"]
        if current+estimate>limit or current+estimate+PAST_KNOWN_USD+PAST_UNKNOWN_HELD_USD>max_total:
            STOP.set();return None
        key=model+"|"+trial["trial_id"]
        if key in STATE["inflight"]:raise RuntimeError("STOP_DUPLICATE_INFLIGHT_REQUEST")
        STATE["inflight"][key]=estimate
        save_ledger("SENDING_"+stage.upper())
        return (key,estimate)

def record_result(stage,trial,model,reservation,payload,response,error,started):
    key,held=reservation
    err=error
    got_model=response.get("model") if isinstance(response,dict) else None
    usage=response.get("usage") if isinstance(response,dict) else None
    usage=usage if isinstance(usage,dict) else {}
    cost=usage.get("cost")
    good_cost=type(cost) in (float,int) and math.isfinite(cost) and 0<=cost<=held
    raw=((response.get("choices") or [{}])[0].get("message") or {}).get("content") if isinstance(response,dict) and isinstance(response.get("choices"),list) and response.get("choices") else None
    choices=response.get("choices") if isinstance(response,dict) else []
    choice_meta=choices[0] if isinstance(choices,list) and choices and isinstance(choices[0],dict) else {}
    letter=raw.strip() if isinstance(raw,str) else ""
    legal={"A","B","T"} if trial["mode"]!="delegated" else {"A","B"}
    valid=(letter in legal and got_model==model and good_cost and
           error is None and not response.get("error") and not choice_meta.get("error") and
           choice_meta.get("finish_reason") not in ("error","length"))
    outcome=None
    if valid:
        outcome= ("Q" if letter==trial["q_label"] else "N") if trial["mode"]=="delegated" else letter
    rec={
      "stage":stage,"model_requested":model,"model_returned":got_model,
      "trial_id":trial["trial_id"],"family_id":trial["family_id"],
      "domain":trial["domain"],"mechanism":trial["mechanism"],
      "mode":trial["mode"],"cost_level":trial["cost_level"],
      "presentation":trial["presentation"],"display_order":trial["display_order"],
      "q_label":trial["q_label"],"n_label":trial["n_label"],
      "request_sha256":trial["request_sha256"],
      "request_messages":[{"role":"system","content":trial["system_message"]},
                          {"role":"user","content":trial["user_message"]}],
      "request_params":{"max_tokens":payload["max_tokens"],
                        "temperature":payload["temperature"],"provider":payload["provider"],
                        "reasoning":payload.get("reasoning")},
      "started_utc":started,"completed_utc":time_utc(),
      "status":"VALID" if valid else "INVALID_OR_UNATTRIBUTABLE",
      "selected_label":letter if valid else None,
      "selected_semantic_action":outcome,
      "arithmetic_correct_answer":trial["arithmetic_control_correct_answer"] if trial["mode"]!="delegated" else None,
      "calibration_is_correct":(letter==trial["arithmetic_control_correct_answer"]) if valid and trial["mode"]!="delegated" else None,
      "transport_error_type":err,
      "raw_response_envelope":response,
      "provider_charged_usd":cost if good_cost else None,
      "conservative_unknown_charge_hold_usd":None if good_cost else held,
      "request_reservation_usd":held,
    }
    with WRITE_LOCK:
        assert key in STATE["inflight"] and STATE["inflight"][key]==held
        STATE["inflight"].pop(key)
        if good_cost:
            STATE["charged_usd"]+=float(cost)
        else:
            STATE["held_unknown_usd"]+=held
        STATE["records_by_stage"][stage]+=1
        with (OUT/(stage+"-responses.jsonl")).open("a",encoding="utf-8") as h:
            h.write(json.dumps(rec,ensure_ascii=False,sort_keys=True)+"\n")
            h.flush();os.fsync(h.fileno())
        save_ledger("CAPTURING_"+stage.upper())
    return rec

def send_one(stage,trial,model,prices,conf):
    reservation=book_reservation(stage,trial,model,prices,conf)
    if reservation is None:return None
    p=prices[model]
    payload={
        "model":model,
        "messages":[{"role":"system","content":trial["system_message"]},
                    {"role":"user","content":trial["user_message"]}],
        "max_tokens":conf["sampling"]["max_completion_tokens"],
        "temperature":conf["sampling"]["temperature"],
        "reasoning":{"enabled":conf["sampling"]["reasoning_enabled"]},
        "provider":{
            "allow_fallbacks":False,
            "sort":conf["sampling"]["provider_sort"],
            "max_price":{"prompt":round(p["input_per_m"]*1.1,6),
                         "completion":round(p["output_per_m"]*1.1,6)},
        },
        "usage":{"include":True},
    }
    started=time_utc()
    response=None;error=None
    try:
        response=http_api("/chat/completions",payload)
    except urllib.error.HTTPError as exc:
        error="HTTP_"+str(exc.code)
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        error="NETWORK_UNCERTAIN_"+type(exc).__name__
    except Exception as exc:
        error="OTHER_"+type(exc).__name__
    return record_result(stage,trial,model,reservation,payload,response,error,started)

def load_records(stage):
    path=OUT/(stage+"-responses.jsonl")
    if not path.exists():return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def by_model(rows):
    return {m:[x for x in rows if x["model_requested"]==m] for m in
            ["openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2"]}

def evaluate_calibration(rows,conf):
    res={}
    gate=conf["calibration"]
    if len(rows)!=864:
        return False,{"reason":"INCOMPLETE_CALIBRATION", "record_count":len(rows)}
    for model,allrows in by_model(rows).items():
        valid=[x for x in allrows if x["status"]=="VALID"]
        controls=[x for x in valid if x["mode"]!="delegated"]
        non_tie=[x for x in controls if x["arithmetic_correct_answer"]!="T"]
        tied=[x for x in controls if x["arithmetic_correct_answer"]=="T"]
        near=[x for x in non_tie if x["cost_level"] in ("below_break_even","above_break_even")]
        rate=lambda a:round(sum(x["calibration_is_correct"] is True for x in a)/len(a),5) if a else 0.0
        valid_rate=len(valid)/len(allrows) if allrows else 0
        dir_domain={}
        for domain in ("continuation","reversibility","verification"):
            chosen={}
            for level in ("very_low","very_high"):
                sub=[x for x in valid if x["domain"]==domain and
                     x["mode"]=="delegated" and x["presentation"]=="time_first" and
                     x["cost_level"]==level]
                chosen[level]=sum(x["selected_semantic_action"]=="Q" for x in sub)/len(sub) if sub else None
            diff=(chosen["very_high"]-chosen["very_low"]) if None not in chosen.values() else None
            sign=(diff if domain=="continuation" else -diff) if diff is not None else None
            dir_domain[domain]={"q_rate_low":chosen["very_low"],
                               "q_rate_high":chosen["very_high"],
                               "expected_direction_margin":sign,
                               "pass":sign is not None and sign>=gate["minimum_direction_diff"]}
        sub_results={
            "attempted":len(allrows),"valid":len(valid),
            "valid_rate":round(valid_rate,5),
            "non_tie_correct":rate(non_tie),"non_tie_n":len(non_tie),
            "tie_correct":rate(tied),"tie_n":len(tied),
            "near_threshold_correct":rate(near),"near_threshold_n":len(near),
            "cost_direction_by_domain":dir_domain,
        }
        sub_results["passed"]=(
            len(allrows)==288 and valid_rate>=gate["min_valid_rate_per_model"] and
            sub_results["non_tie_correct"]>=gate["min_explicit_control_non_tie_accuracy_per_model"] and
            sub_results["tie_correct"]>=gate["min_explicit_control_tie_accuracy_per_model"] and
            sub_results["near_threshold_correct"]>=gate["min_near_threshold_explicit_control_accuracy_per_model"] and
            sum(v["pass"] for v in dir_domain.values())>=gate["min_cost_direction_domains_per_model"]
        )
        res[model]=sub_results
    passed=all(x["passed"] for x in res.values())
    return passed,res

def budget_preflight_for_main(cal_rows,prices,main_rows,conf):
    p95s={}
    for m,x in by_model(cal_rows).items():
        costs=sorted(rec["provider_charged_usd"] for rec in x
                     if rec["provider_charged_usd"] is not None)
        if len(costs)<270: return False,{"reason":"INSUFFICIENT_BILLED_CALIBRATION_FOR_FORECAST"}
        idx=math.ceil(len(costs)*0.95)-1
        p95s[m]=costs[idx]
    full=0.0
    by={}
    for m in conf["model_roster"]:
        forecast=max(p95s[m],0.00015)*1680*1.5
        by[m]=round(forecast,7);full+=forecast
    current=STATE["charged_usd"]+STATE["held_unknown_usd"]
    buffer=0.12
    limit=min(conf["budget"]["new_v3_1_spending_cap_usd"],
              conf["budget"]["global_project_cap_usd"]-PAST_KNOWN_USD-PAST_UNKNOWN_HELD_USD)
    # Reserve actual spare budget for accounted-but-unknown individual responses.
    return full+current+buffer<=limit,{
        "per_model_p95_calibration_usd":p95s,
        "projected_main_at_1_5_x_p95_calibration_usd":round(full,6),
        "per_model_forecast_usd":by,"known_spend_plus_unknown_holds":round(current,6),
        "required_spare_buffer_usd":buffer,"incremental_ceiling":limit,
        "preflight_passed":full+current+buffer<=limit,
        "forecast_is_not_a_guaranteed_future_bill":True,
    }

def summarize_main(records,conf):
    report={"attempted":len(records),"expected":5040,
            "valid":sum(x["status"]=="VALID" for x in records),
            "models":{},"outcomes":{},"framing_pairs":{}}
    for model,x in by_model(records).items():
        good=[r for r in x if r["status"]=="VALID"]
        report["models"][model]={"attempted":len(x),"valid":len(good),
                                 "known_charges":round(sum(r["provider_charged_usd"] or 0 for r in x),7)}
        report["outcomes"][model]={}
        report["framing_pairs"][model]={}
        for dom in ("continuation","reversibility","verification"):
            report["outcomes"][model][dom]={}
            for level in ("very_low","below_break_even","break_even","above_break_even","very_high"):
                sub=[r for r in good if r["domain"]==dom and r["cost_level"]==level
                     and r["presentation"]=="time_first"]
                report["outcomes"][model][dom][level]={
                    "n":len(sub),"q_count":sum(r["selected_semantic_action"]=="Q" for r in sub),
                    "q_rate":round(sum(r["selected_semantic_action"]=="Q" for r in sub)/len(sub),4) if sub else None}
            frame_rows=[r for r in x if r["domain"]==dom and r["cost_level"] in
                        ("below_break_even","above_break_even")]
            groups=collections.defaultdict(dict)
            for r in frame_rows:
                key=(r["family_id"],r["cost_level"],r["q_label"],r["display_order"])
                groups[key][r["presentation"]]=r
            contrasts=[]
            missing_pairs=0
            for pair in groups.values():
                a=pair.get("risk_first");b=pair.get("time_first")
                if a and b and a["status"]=="VALID" and b["status"]=="VALID":
                    contrasts.append((a["selected_semantic_action"]=="Q")-
                                     (b["selected_semantic_action"]=="Q"))
                else:missing_pairs+=1
            report["framing_pairs"][model][dom]={
                "complete":len(contrasts),"missing":missing_pairs,
                "risk_minus_time_effect":round(statistics.mean(contrasts),5) if contrasts else None,
                "worst_case_bounds":[round((sum(contrasts)-missing_pairs)/max(1,len(contrasts)+missing_pairs),5),
                                     round((sum(contrasts)+missing_pairs)/max(1,len(contrasts)+missing_pairs),5)],
            }
    return report

def run_stage(stage,conf):
    global SECRET
    SECRET=os.environ.get("OPENROUTER_API_KEY","")
    if len(SECRET)<12:raise RuntimeError("STOP_NO_INFERENCE_KEY")
    start_state(stage)
    prices=model_prices(conf["model_roster"])
    key_cap=key_remaining()
    if key_cap < 0.20:raise RuntimeError("STOP_KEY_AVAILABLE_TOO_LOW")
    trials=build(stage)
    expected=len(trials)*len(conf["model_roster"])
    if stage=="main":
        cal=json.loads((OUT/"calibration-report.json").read_text())
        if not cal["passed_all_gates"] or not cal["main_cost_preflight"]["preflight_passed"]:
            raise RuntimeError("STOP_MAIN_GATE_NOT_PASSED")
    plan=[(x,model) for x in trials for model in conf["model_roster"]]
    if stage=="main" and expected!=5040:raise RuntimeError("STOP_MAIN_WRONG_REQUEST_COUNT")
    if stage=="calibration" and expected!=864:raise RuntimeError("STOP_CAL_WRONG_REQUEST_COUNT")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=conf["sampling"]["max_concurrent_requests"]) as pool:
            futures=[pool.submit(send_one,stage,x,model,prices,conf) for x,model in plan]
            for idx,fut in enumerate(concurrent.futures.as_completed(futures),1):
                try:
                    fut.result()
                except Exception as exc:
                    STOP.set()
                    print(json.dumps({"critical_error":type(exc).__name__,"stage":stage}),flush=True)
                if idx%200==0 or idx==expected:
                    print(json.dumps({
                        "phase":stage,"finished_requests":idx,"total":expected,
                        "known_spent_usd":round(STATE["charged_usd"],5),
                        "unknown_hold_usd":round(STATE["held_unknown_usd"],5),
                        "stopped":STOP.is_set()
                    }),flush=True)
        records=load_records(stage)
        if stage=="calibration":
            passed,gate=evaluate_calibration(records,conf)
            preflight=(False,{"reason":"CALIBRATION_DID_NOT_PASS"})
            if passed and not STOP.is_set():
                preflight=budget_preflight_for_main(records,prices,build("main"),conf)
            passed=passed and preflight[0] and not STOP.is_set()
            report={"stage":"calibration","attempted":len(records),
                    "expected_attempts":864,"passed_all_gates":passed,
                    "calibration_gates":gate,"main_cost_preflight":preflight[1],
                    "known_charges_usd":round(STATE["charged_usd"],9),
                    "held_unknown_usd":round(STATE["held_unknown_usd"],9),
                    "protocol_id":conf["protocol_id"]}
            jsonwrite(OUT/"calibration-report.json",report)
            with WRITE_LOCK:save_ledger("CALIBRATION_COMPLETE_GATE_PASS" if passed else "CALIBRATION_COMPLETE_NO_GO")
            print(json.dumps({"phase":stage,"pass":passed,
                              "gates":gate,"budget_preflight":preflight[1]},sort_keys=True),flush=True)
            with open(os.environ.get("GITHUB_OUTPUT","/tmp/v3_1_go_state.txt"),"a") as h:
                h.write("go="+("true" if passed else "false")+"\n")
            return 0 # Valid NO-GO is a normal diagnostic outcome.
        else:
            rep=summarize_main(records,conf)
            completed=(len(records)==5040 and not STOP.is_set())
            report={"stage":"main","protocol_id":conf["protocol_id"],
                    "status":"COMPLETE" if completed else "PARTIAL_STOP",
                    "details":rep,"known_charges_total_usd":round(STATE["charged_usd"],9),
                    "held_unknown_usd":round(STATE["held_unknown_usd"],9)}
            jsonwrite(OUT/"main-report.json",report)
            with WRITE_LOCK:save_ledger("MAIN_COMPLETE" if completed else "MAIN_PARTIAL_STOP")
            return 0 if completed else 2
    finally:
        print(json.dumps({"stage":stage,"known_usd":round(STATE["charged_usd"],8),
                          "held_unknown_usd":round(STATE["held_unknown_usd"],8),
                          "inflight":len(STATE["inflight"])}),flush=True)

def mock():
    conf=verify_freeze()
    cal=build("calibration");main=build("main")
    assert len(cal)==288 and len(main)==1680
    def fake(trial,model,decision=None,cost=0.0005):
        opt=trial["arithmetic_control_correct_answer"] if trial["mode"]!="delegated" else (
            trial["q_label"] if
            (trial["domain"]=="continuation" and trial["cost_level"] in ("very_high","above_break_even")) or
            (trial["domain"]!="continuation" and trial["cost_level"] in ("very_low","below_break_even"))
            else trial["n_label"])
        return {"model_requested":model,"provider_charged_usd":cost,
                "status":"VALID","mode":trial["mode"],"domain":trial["domain"],
                "family_id":trial["family_id"],"cost_level":trial["cost_level"],
                "presentation":trial["presentation"],"display_order":trial["display_order"],
                "q_label":trial["q_label"],"selected_semantic_action":(
                    "Q" if opt==trial["q_label"] else "N"),
                "calibration_is_correct":(opt==trial["arithmetic_control_correct_answer"]),
                "arithmetic_correct_answer":trial["arithmetic_control_correct_answer"]}
    rows=[fake(x,m) for x in cal for m in conf["model_roster"]]
    passed,gates=evaluate_calibration(rows,conf)
    assert passed, gates
    # Honest cost rules: calibration pass alone never bypasses main budget preflight.
    return {"mock_pass":True,"calibration_rows":len(rows),
            "project_ceiling":conf["budget"]["global_project_cap_usd"],
            "new_spend_ceiling":conf["budget"]["new_v3_1_spending_cap_usd"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("mock","calibration","main"),required=True)
    args=p.parse_args()
    if args.stage=="mock":
        print(json.dumps(mock(),sort_keys=True));return 0
    conf=verify_freeze()
    return run_stage(args.stage,conf)

if __name__=="__main__":
    raise SystemExit(main())
