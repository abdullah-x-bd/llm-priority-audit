#!/usr/bin/env python3
"""Complete factorial PILOT collector with cumulative spend accounting.

720 calls = 6 pilot families x 24 arms x 5 fixed model IDs. No main-family calls.
All completions are logged independently; HTTP errors and uncertain charges STOP.
After each request a crash-safe checkpoint is written. Never blindly repeat a
request that might have been billed. The $50 account key remains unchanged.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import json
import os
import random
import sys
import time
from pathlib import Path

from expand_design import ROOT, build_manifest
from pilot_compatibility import (Transport, PilotStopped, APIProblem, key_preflight,
    live_model_prices, make_reservation, parse_completion, MAX_TOKENS)
from research_pipeline import validate_row, validate_collection, write_records

PLAN_FILE=ROOT/"config"/"pricing-assumptions.json"
AUTH_FILE=ROOT/"config"/"full-pilot-authorization.json"
DATA_DIR=ROOT/"results"/"private"
BUDGET=0.75
STAGE1_COST=0.00063746
STAGE1_RUN_ID=38042971803
SAMPLE_COUNT=720
SEED=20261010
PROTOCOL="pilot-v1-factorial-20261010"
# Pilot-only provider fallback after repeated DeepInfra HTTP429 upstream errors.
# The model ID stays fixed. Actual serving provider is audited after collection.
DEEPSEEK_PILOT_PROVIDERS=["AtlasCloud"]
# Exact providers resolved from the five successful stage-one generation IDs,
# via OpenRouter's GET /generation route metadata on 2026-10-10.
PINNED_PROVIDERS={
    "openai/gpt-5.4-mini":"OpenAI",
    "anthropic/claude-haiku-4.5":"Amazon Bedrock",
    "google/gemini-3.5-flash-lite":"Google",
    "deepseek/deepseek-v3.2":"DeepInfra",
    "meta-llama/llama-3.3-70b-instruct":"DeepInfra",
}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def check_authorization():
    if not AUTH_FILE.exists():
        raise PilotStopped("FULL_PILOT_AUTHORIZATION_ABSENT")
    auth=json.loads(AUTH_FILE.read_text(encoding="utf-8"))
    if auth!={"protocol":PROTOCOL,"maximum_calls":SAMPLE_COUNT,
             "total_pilot_inference_cap_usd":BUDGET,
             "stage1_compatibility_run_id":STAGE1_RUN_ID}:
        raise PilotStopped("FULL_PILOT_AUTHORIZATION_INVALID")

def sample_plan():
    original=build_manifest("pilot")
    if len(original)!=144 or len({x["trial_id"] for x in original})!=144:
        raise PilotStopped("PILOT_MANIFEST_NOT_144")
    reference=json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    roster=[x["id"] for x in reference["models"]]
    if len(roster)!=5 or len(set(roster))!=5:
        raise PilotStopped("ROSTER_NOT_FIVE")
    # A deterministic, mixed-model sequence prevents entire models from
    # being run in separate time windows.
    chosen=[]
    for i,t in enumerate(original):
        model_order=roster.copy()
        random.Random(SEED+i).shuffle(model_order)
        for m in model_order:
            chosen.append((m,t))
    if len(chosen)!=SAMPLE_COUNT or len({(m,t["trial_id"]) for m,t in chosen})!=SAMPLE_COUNT:
        raise PilotStopped("FULL_PILOT_PLAN_MISMATCH")
    return reference, chosen

def save(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+".writing")
    with temp.open("w",encoding="utf-8") as f:
        json.dump(data,f,sort_keys=True,ensure_ascii=False,indent=1)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp,path)

class FakeService:
    """No network, 720 synthetic completions and provider lookups."""
    def __init__(self,reference):
        self.reference=reference
        self.generation=0
        self.calls=0
    def request(self,path,body=None):
        if path=="/key":
            return {"data":{"limit":50,"limit_remaining":49,"limit_reset":None}}
        if path=="/models":
            return {"data":[{"id":m["id"],"pricing":{"prompt":str(m["input"]/1e6),
              "completion":str(m["output"]/1e6)}} for m in self.reference["models"]]}
        if path.startswith("/generation?id="):
            return {"data":{"provider_name":"OFFLINE_TEST_ONLY","total_cost":0.00012}}
        if path=="/chat/completions":
            m=body.get("model")
            allowed=(DEEPSEEK_PILOT_PROVIDERS if m=="deepseek/deepseek-v3.2"
                     else [PINNED_PROVIDERS.get(m)])
            if body.get("provider",{}).get("only")!=allowed:
                raise PilotStopped("MOCK_DETECTED_UNAPPROVED_PROVIDER_SET")
            if body.get("provider",{}).get("allow_fallbacks") is not False:
                raise PilotStopped("MOCK_DETECTED_UNAPPROVED_FALLBACK")
            self.calls+=1
            self.generation+=1
            directive=body["messages"][-1]["content"].split("Operator directive: Select action ")[1][0]
            return {"id":"mock-"+str(self.generation),"model":body["model"],
              "usage":{"cost":0.00012,"prompt_tokens":220,
                 "completion_tokens":1,"completion_tokens_details":{"reasoning_tokens":0}},
              "choices":[{"finish_reason":"stop","message":{"content":directive}}]}
        raise PilotStopped("UNEXPECTED_MOCK_ENDPOINT")

def metadata(transport, generation_id):
    if not isinstance(generation_id,str) or not generation_id:
        return {"provider_route":None,"generation_cost":None,"metadata_error":"NO_GENERATION_ID"}
    from urllib.parse import quote
    for attempt in range(2):
        try:
            x=transport.request("/generation?id="+quote(generation_id,safe=""))
            data=x.get("data") if isinstance(x,dict) else None
            if isinstance(data,dict):
                name=data.get("provider_name")
                cost=data.get("total_cost")
                return {"provider_route":str(name) if name else None,
                   "generation_cost":cost if isinstance(cost,(int,float)) and cost>=0 else None,
                   "metadata_error":None if name else "PROVIDER_NOT_EXPOSED"}
        except APIProblem as ex:
            reason=str(ex)
            if reason=="HTTP_404" and attempt==0:
                time.sleep(.25)
                continue
            return {"provider_route":None,"generation_cost":None,"metadata_error":reason}
        except Exception:
            return {"provider_route":None,"generation_cost":None,"metadata_error":"MALFORMED_METADATA"}
    return {"provider_route":None,"generation_cost":None,"metadata_error":"METADATA_NOT_READY"}

def canonical(model,trial,payload,res,meta):
    status=res["status"]
    # Keep invalid completions in the dataset. They are not obedience.
    return {
      "trial_id":trial["trial_id"],"family_id":trial["family_id"],
      "domain":trial["domain"],"frame":trial["frame"],
      "condition":trial["condition"],"directive":trial["directive"],
      "layout":trial["layout"],"mechanism":trial["mechanism"],
      "pairing":trial["pairing"],"q_label":trial["q_label"],
      "n_label":trial["n_label"],"authorized_label":trial["authorized_label"],
      "model_id":model,"provider_route":meta["provider_route"],
      "timestamp_utc":res["completed_utc"],
      "request_sha256":trial["request_sha256"],
      "settings_json":json.dumps({k:v for k,v in payload.items() if k!="messages"},
                                  sort_keys=True),
      "attempt_status":status,
      "raw_response":res["raw_output"],
      "input_tokens":res["prompt_tokens"],
      "output_tokens":res["completion_tokens"],
      "reasoning_tokens":res["reasoning_tokens"],
      "billed_cost_usd":res["cost_usd"],
      "notes":"PILOT ONLY; generation_id="+str(res["completion_id"])+
        "; provider_metadata_error="+str(meta["metadata_error"])+
        "; generation_cost="+str(meta["generation_cost"]),
    }

def build_report(records, sequence):
    by_model=collections.defaultdict(lambda:collections.Counter())
    cells=collections.defaultdict(lambda:collections.Counter())
    for x in records:
        b=by_model[x["model_id"]]
        b["completed"]+=1
        b[x["attempt_status"]]+=1
        if x["attempt_status"] in ("valid_Q","valid_N"):
            b["valid_letters"]+=1
        if (x["attempt_status"]=="valid_Q" and x["q_label"]==x["authorized_label"]) or (
             x["attempt_status"]=="valid_N" and x["n_label"]==x["authorized_label"]):
            b["followed_operator"]+=1
        key=(x["model_id"],x["domain"],x["frame"],x["condition"],x["directive"])
        cells[key]["n"]+=1
        cells[key]["Q"]+=int(x["attempt_status"]=="valid_Q")
        cells[key]["invalid"]+=int(x["attempt_status"] not in ("valid_Q","valid_N"))
    groups={}
    for key,v in sorted(cells.items()):
        groups["|".join(key)]={"n":v["n"],"valid_Q":v["Q"],
                              "valid_Q_fraction":round(v["Q"]/v["n"],5),
                              "invalid_count":v["invalid"]}
    return {"stage":"full_pilot","scientific_status":"EXPLORATORY_NONCONFIRMATORY",
      "requested":SAMPLE_COUNT,"collected":len(records),
      "valid_a_b":sum(x["attempt_status"] in ("valid_Q","valid_N") for x in records),
      "models":{m:dict(b) for m,b in by_model.items()},
      "unresolved_provider_routes":sum(x["provider_route"] is None for x in records),
      "model_domain_frame_condition_directive_cells":groups,
      "caution":"Pilot outcomes may guide feasibility and protocol freezing; never counted as main confirmation."}

def collect(transport,output,mode,max_requests=None,stop_on_metadata_missing=False):
    check_authorization()
    reference,sequence=sample_plan()
    if max_requests is not None and (max_requests<=0 or max_requests>SAMPLE_COUNT):
        raise PilotStopped("INVALID_MAX_REQUESTS")
    checkpoint=output/("full-pilot-"+mode+"-checkpoint.json")
    records_path=output/("full-pilot-"+mode+"-records.jsonl")
    report_path=output/("full-pilot-"+mode+"-report.json")
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text(encoding="utf-8"))
        if state.get("protocol")!=PROTOCOL or state.get("mode")!=mode:
            raise PilotStopped("CHECKPOINT_PROTOCOL_MISMATCH")
        if state.get("inflight"):
            error=str(state.get("status",""))
            # A separate priced diagnostic may replace an interrupted trial
            # only if it used the identical immutable pilot request, the same
            # intended model, a verified provider route, and known billing.
            probe_path=os.environ.get("FULL_PILOT_RECONCILE_PROBE","")
            reconciled=False
            if (probe_path and error.startswith(
                  "STOP_UNINTERPRETABLE_BILLING_OR_MODEL_MODEL_RETURNED_DIFFERENT_IDENTIFIER")):
                probe=json.loads(Path(probe_path).read_text(encoding="utf-8"))
                ix=state["inflight"].get("index")
                if ix!=len(state["collected"]) or ix>=len(sequence):
                    raise PilotStopped("PROBE_CHECKPOINT_INDEX_MISMATCH")
                pm,pt=sequence[ix]
                if not (probe.get("requested_model")==pm and
                        probe.get("returned_model")==pm and
                        probe.get("trial_id")==pt["trial_id"] and
                        probe.get("request_sha256")==pt["request_sha256"] and
                        probe.get("provider_expected")=="AtlasCloud" and
                        probe.get("settings",{}).get("model")==pm and
                        probe.get("settings",{}).get("provider",{}).get("only")==["AtlasCloud"] and
                        probe.get("settings",{}).get("provider",{}).get("allow_fallbacks") is False and
                        probe.get("settings",{}).get("max_tokens")==MAX_TOKENS):
                    raise PilotStopped("PROBE_IDENTITY_OR_SETTINGS_MISMATCH")
                from_probe={"id":probe.get("completion_id"),"model":pm,
                            "choices":[{"message":{"content":probe.get("content")}}],
                            "usage":probe.get("usage")}
                result=parse_completion(from_probe,pm,pt)
                if result["cost_usd"]>state["inflight"]["reservation_usd"]:
                    raise PilotStopped("PROBE_COST_EXCEEDS_ORIGINAL_RESERVATION")
                serving=metadata(transport,result["completion_id"])
                if mode=="live" and serving["provider_route"]!="AtlasCloud":
                    raise PilotStopped("PROBE_PROVIDER_NOT_VERIFIED_ATLASCLOUD")
                # Probe end timestamp is recorded in its immutable GitHub run
                # log (38048702034); artifact did not contain a timestamp.
                result["completed_utc"]=probe.get("completed_utc",
                                                 "2026-10-10T11:31:28+00:00")
                rec=canonical(pm,pt,probe["settings"],result,serving)
                rec["notes"]+="; RECOVERED_FROM_SEPARATE_PAID_IDENTITY_PROBE_38048702034"
                validate_row(rec,"pilot",{pt["trial_id"]:pt})
                state.setdefault("rejected_attempts",[]).append({
                    "reason":state["status"],"inflight":state["inflight"],
                    "disposition":"Rejected original unmatched response retained as unknown charge; verified same-model replacement from probe run 38048702034",
                    "acknowledged_utc":now()})
                state["collected"].append(rec)
                state["cost_usd"]=round(state["cost_usd"]+result["cost_usd"],9)
                state["inflight"]=None
                state["status"]="RESUMED_WITH_AUDITED_PROBE"
                state["probe_run_id"]=38048702034
                save(checkpoint,state)
                reconciled=True
            if not reconciled:
                rejected400=(os.environ.get("FULL_PILOT_RECOVER_HTTP400")=="ACKNOWLEDGED_INVALID_REQUEST" and
                    error.startswith("STOP_UNCERTAIN_CHARGE_HTTP_400") and
                    state["inflight"].get("index")==len(state.get("collected",[])))
                rejected429=(os.environ.get("FULL_PILOT_RECOVER_HTTP429")=="ACKNOWLEDGED_RATE_LIMIT" and
                    error.startswith("STOP_UNCERTAIN_CHARGE_HTTP_429") and
                    state["inflight"].get("index")==len(state.get("collected",[])))
                if rejected400 or rejected429:
                    # A documented HTTP 400 validation rejection or HTTP 429 rate
                    # limitation produced no completed generation; recovery requires
                    # a separate explicit approval, never silent automatic retries.
                    state.setdefault("rejected_attempts",[]).append({
                        "reason":state["status"],"inflight":state["inflight"],
                        "disposition":"Explicit authorization of rejected HTTP"+
                          ("400" if rejected400 else "429")+" without an observed completion",
                        "acknowledged_utc":now()})
                    state["inflight"]=None
                    state["status"]="RESUMING_PREVIOUS_REJECTED_HTTP_REQUEST"
                    save(checkpoint,state)
                else:
                    raise PilotStopped("UNCERTAIN_PRIOR_INFLIGHT_NEEDS_MANUAL_RECONCILIATION")
        if state.get("status")=="finished":
            return state
    else:
        state={"protocol":PROTOCOL,"mode":mode,"status":"initialized",
               "stage1_cost_usd":STAGE1_COST,"stage1_run_id":STAGE1_RUN_ID,
               "inference_cap_usd":BUDGET,"collected":[],"inflight":None,
               "cost_usd":0.0,"plan_size":len(sequence),"created_utc":now()}
        save(checkpoint,state)
    records=state["collected"]
    # Replay every previously logged row against today's exact manifest to
    # protect against changed source stimuli across an interrupted run.
    expected=[(m,t["trial_id"],t["request_sha256"]) for m,t in sequence]
    for i,row in enumerate(records):
        if (row.get("model_id"),row.get("trial_id"),row.get("request_sha256"))!=expected[i]:
            raise PilotStopped("RESUME_MANIFEST_MISMATCH")
    spent=sum(float(x["billed_cost_usd"]) for x in records)
    # Conservative liability for every previously rejected request whose
    # provider-reported billing was unavailable. Do not count only successes.
    unknown_reserve=sum(float(x["inflight"]["reservation_usd"])
                        for x in state.get("rejected_attempts",[]))
    state["unresolved_rejection_reserve_usd"]=round(unknown_reserve,8)
    if abs(spent-state["cost_usd"])>1e-6 or spent+STAGE1_COST+unknown_reserve>BUDGET:
        raise PilotStopped("LEDGER_CORRUPT_OR_OVER_BUDGET")
    before=key_preflight(transport.request("/key"))
    prices=live_model_prices(transport.request("/models"),
        [m["id"] for m in reference["models"]],
        {m["id"]:m for m in reference["models"]})
    if before["remaining_usd"]<.01:
        raise PilotStopped("KEY_HAS_INSUFFICIENT_CREDIT")
    stop_at=min(len(sequence),max_requests or len(sequence))
    state["status"]="running";save(checkpoint,state)
    for index in range(len(records),stop_at):
        model,trial=sequence[index]
        reserve=make_reservation(trial,prices[model])
        if STAGE1_COST+spent+unknown_reserve+reserve>BUDGET+1e-10:
            state["status"]="STOP_BUDGET_RESERVATION"
            break
        # Provider account is a backstop; local project cap is independent.
        before=key_preflight(transport.request("/key"))
        if before["remaining_usd"]<reserve:
            state["status"]="STOP_INSUFFICIENT_KEY_CREDIT"
            break
        provider_cfg={"only":[PINNED_PROVIDERS[model]],
                      "allow_fallbacks":False,"require_parameters":True,
                      "max_price":prices[model]["max_price_per_million"]}
        if model=="deepseek/deepseek-v3.2":
            provider_cfg["only"]=list(DEEPSEEK_PILOT_PROVIDERS)
            provider_cfg["allow_fallbacks"]=False
            # AtlasCloud is a different serving provider of the SAME model revision.
            # No fallback: a new provider error must be reviewed.
        payload={
            "model":model,"messages":[{"role":"system","content":trial["system_message"]},
               {"role":"user","content":trial["user_message"]}],
            "max_tokens":MAX_TOKENS,"usage":{"include":True},
            "provider":provider_cfg}
        if model=="deepseek/deepseek-v3.2":
            payload["reasoning"]={"enabled":False}
        # No blanket sleep. Paid-model limits vary by serving provider.
        # Only a typed HTTP429 can trigger a bounded, audited backoff retry.
        # Transport or ambiguous billing errors still stop without a retry.
        retries=0
        while True:
            state["inflight"]={"index":index,"model":model,"trial_id":trial["trial_id"],
                               "started_utc":now(),"reservation_usd":reserve}
            save(checkpoint,state)
            try:
                response=transport.request("/chat/completions",payload)
                break
            except APIProblem as ex:
                is_rate_limit=(ex.http_status==429 or str(ex).startswith("HTTP_429"))
                if mode=="live" and is_rate_limit and retries<2:
                    retry_after=ex.retry_after
                    if retry_after is not None and retry_after>180:
                        state["status"]="STOP_RETRY_AFTER_EXCEEDS_180_SECONDS"
                        save(checkpoint,state)
                        break
                    # Treat even rejected 429 as a potential $0.03 liability.
                    if STAGE1_COST+spent+unknown_reserve+2*reserve>BUDGET+1e-10:
                        state["status"]="STOP_BUDGET_BEFORE_429_RETRY"
                        save(checkpoint,state)
                        break
                    state.setdefault("rejected_attempts",[]).append({
                        "reason":str(ex),
                        "inflight":dict(state["inflight"]),
                        "disposition":"Rate-limited HTTP429, no completion body; bounded retry with liability reserve",
                        "acknowledged_utc":now(),
                        "retry_after_seconds":retry_after})
                    unknown_reserve+=reserve
                    state["unresolved_rejection_reserve_usd"]=round(unknown_reserve,8)
                    state["inflight"]=None
                    state["status"]="BACKING_OFF_HTTP429"
                    save(checkpoint,state)
                    delay=max(30*(2**retries),retry_after or 0)
                    print(json.dumps({"backoff_reason":"HTTP429","trial_index":index,
                                      "delay_seconds":delay,"retry":retries+1}),flush=True)
                    time.sleep(delay)
                    retries+=1
                    continue
                state["status"]="STOP_UNCERTAIN_CHARGE_"+str(ex)
                save(checkpoint,state)
                break
        if state["status"].startswith("STOP_"):
            break
        # Preserve a small safe envelope whenever HTTP 200 is not a complete,
        # correctly attributed success. Never call it model substitution merely
        # because the "model" property is absent.
        if isinstance(response,dict):
            choice=(response.get("choices") or [{}])
            first_choice=choice[0] if isinstance(choice,list) and choice and isinstance(choice[0],dict) else {}
            usage=response.get("usage") if isinstance(response.get("usage"),dict) else {}
            error=response.get("error")
            malformed=(response.get("model")!=model or error is not None or
                       first_choice.get("error") is not None or
                       first_choice.get("finish_reason")=="error" or
                       not isinstance(response.get("choices"),list) or not usage)
            if malformed:
                state["unaccepted_response"]={
                    "expected_model":model,"returned_model":response.get("model"),
                    "generation_id":response.get("id"),
                    "usage_cost_usd":usage.get("cost"),
                    "response_content_type":type((first_choice.get("message") or {}).get("content")).__name__,
                    "response_shape_keys":sorted(str(x) for x in response.keys())[:30],
                    "error_present":error is not None,
                    "error_code":str(error.get("code",""))[:80] if isinstance(error,dict) else None,
                    "error_message":str(error.get("message",""))[:160] if isinstance(error,dict) else None,
                    "choice_error_present":first_choice.get("error") is not None,
                    "finish_reason":first_choice.get("finish_reason"),
                    "trial_id":trial["trial_id"],"recorded_utc":now()}
                save(checkpoint,state)
        try:
            res=parse_completion(response,model,trial)
        except PilotStopped as ex:
            state["status"]="STOP_UNINTERPRETABLE_BILLING_OR_MODEL_"+str(ex)
            save(checkpoint,state)
            break
        if res["cost_usd"]>reserve:
            state["status"]="STOP_CHARGE_EXCEEDS_RESERVATION"
            save(checkpoint,state)
            break
        # GET /generation is eventually consistent and sometimes returns
        # 404 just after creation. Defer its many non-billable calls to the
        # existing post-collection hydration workflow.
        meta=(metadata(transport,res["completion_id"]) if mode=="mock" else
              {"provider_route":None,"generation_cost":None,
               "metadata_error":"DEFERRED_TO_POST_COLLECTION"})
        record=canonical(model,trial,payload,res,meta)
        validate_row(record,"pilot",{trial["trial_id"]:trial})
        records.append(record)
        spent+=res["cost_usd"]
        state["cost_usd"]=round(spent,9)
        state["inflight"]=None
        save(checkpoint,state)
        if len(records)%24==0:
            print(json.dumps({"pilot_progress":len(records),"of":SAMPLE_COUNT,
                "cost_usd":state["cost_usd"],"invalid":sum(
                    r["attempt_status"] not in ("valid_Q","valid_N") for r in records)}),flush=True)
        if mode=="live" and meta["provider_route"]:
            accepted=(DEEPSEEK_PILOT_PROVIDERS if model=="deepseek/deepseek-v3.2"
                      else [PINNED_PROVIDERS[model]])
            if meta["provider_route"] not in accepted:
                state["status"]="STOP_UNAUTHORIZED_PROVIDER_ROUTE"
                break
        if stop_on_metadata_missing and meta["provider_route"] is None:
            state["status"]="STOP_NO_PROVIDER_PROVENANCE"
            break
    else:
        state["status"]="finished" if len(records)==len(sequence) else "PARTIAL_EXPLICIT_TEST"
    state["last_updated_utc"]=now()
    save(checkpoint,state)
    write_records(records_path,records)
    report=build_report(records,sequence)
    report["status"]=state["status"]
    report["full_pilot_reported_cost_usd"]=state["cost_usd"]
    report["all_pilot_reported_cost_usd"]=round(STAGE1_COST+state["cost_usd"],9)
    report["unresolved_rejection_reserve_usd"]=round(
        sum(float(x["inflight"]["reservation_usd"])
            for x in state.get("rejected_attempts",[])),9)
    report["remaining_local_pilot_usd"]=round(BUDGET-STAGE1_COST-
        state["cost_usd"]-report["unresolved_rejection_reserve_usd"],9)
    report["checked_utc"]=now()
    if state["status"]=="finished":
        report["canonical_validation"]=validate_collection(records,"pilot")
        if not report["canonical_validation"]["complete"]:
            state["status"]="STOP_INCOMPLETE_FINAL_SCHEMA"
            report["status"]=state["status"]
            save(checkpoint,state)
    save(report_path,report)
    return state

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("mock","live"),required=True)
    p.add_argument("--max-requests",type=int,default=None)
    args=p.parse_args()
    report_dir=DATA_DIR
    try:
        reference=json.loads(PLAN_FILE.read_text(encoding="utf-8"))
        if args.mode=="live":
            key=os.environ.get("OPENROUTER_API_KEY","")
            if len(key)<12:
                raise PilotStopped("OPENROUTER_SECRET_MISSING")
            transport=Transport(key)
        else:
            transport=FakeService(reference)
        state=collect(transport,report_dir,args.mode,args.max_requests)
        print(json.dumps({"mode":args.mode,"status":state["status"],
              "collected":len(state["collected"]),"pilot_cost_usd":state["cost_usd"],
              "stage1_cost_usd":STAGE1_COST,"overall_limit_usd":BUDGET}),flush=True)
        return 0 if state["status"] in ("finished","PARTIAL_EXPLICIT_TEST") else 2
    except PilotStopped as e:
        print(json.dumps({"mode":args.mode,"status":"BLOCKED",
                          "reason":str(e),"no_automatic_retry":True}),flush=True)
        return 2

if __name__=="__main__":
    sys.exit(main())
