#!/usr/bin/env python3
"""Capture-first, fail-closed 240-response held-out v2 sensitivity calibration.

6 distinct never behavior-tested contexts x 2 lexical frames x 2 directives x
2 layouts x 5 fixed models. Does not touch v2 main stimuli or execute main.
The source manifests and numerical gate were defined before model outcomes.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,os,random,sys
from pathlib import Path
from datetime import datetime,timezone

from expand_design import ROOT
from v2_sensitivity_manifest import manifest
from pilot_compatibility import Transport,APIProblem,PilotStopped,key_preflight,live_model_prices,make_reservation,parse_completion
from full_pilot import PINNED_PROVIDERS,PLAN_FILE
from raw_capture import cost_from_response

OUT=ROOT/"results"/"private"/"v2-calibration"
CHECKPOINT=OUT/"live-checkpoint.json"
SENSITIVITY_CAP_USD=.50
GLOBAL_CAP_USD=8.0
PAST_WORST_CASE=.51196256+.225477+.0904+.081715
TOKEN_MAX=64
SEED=20261011
PROTOCOL="v2-calibration-draft-20261010"
VALID={"valid_Q","valid_N"}

def sequence():
    roster=json.loads(PLAN_FILE.read_text(encoding="utf-8"))["models"]
    models=[x["id"] for x in roster]
    trials=manifest()
    jobs=[]
    for i,t in enumerate(trials):
        shuffled=models.copy()
        random.Random(SEED+i).shuffle(shuffled)
        jobs.extend((m,t) for m in shuffled)
    assert len(jobs)==240
    assert len(set((m,t["trial_id"]) for m,t in jobs))==240
    return jobs

def save(x):
    OUT.mkdir(parents=True,exist_ok=True)
    p=CHECKPOINT.with_suffix(".tmp")
    with p.open("w",encoding="utf-8") as f:
        json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=1)
        f.flush();os.fsync(f.fileno())
    os.replace(p,CHECKPOINT)

def new_state():
    return {"protocol":PROTOCOL,"results":[],"inflight":None,
        "known_cost_usd":0.0,"uncertain_reserve_usd":0.0,
        "max_calibration_usd":SENSITIVITY_CAP_USD,
        "prior_worst_case_research_usd":PAST_WORST_CASE,
        "main_runs_started":0,"status":"starting",
        "started_utc":datetime.now(timezone.utc).isoformat()}

def classify(response,model,t):
    meta={
       "model":model,"trial_id":t["trial_id"],"request_sha256":t["request_sha256"],
       "frame":t["frame"],"directive":t["directive"],"domain":t["domain"],
       "family_id":t["family_id"],"layout":t["layout"],"authorized_label":t["authorized_label"],
       "q_label":t["q_label"],"n_label":t["n_label"],"status":"unresolved",
       "choice":None,"cost_usd":None,"returned_model":None,"generation_id":None,
       "raw_response":response,"recorded_utc":datetime.now(timezone.utc).isoformat(),
    }
    if isinstance(response,dict):
        meta["returned_model"]=response.get("model")
        meta["generation_id"]=response.get("id")
        meta["cost_usd"]=cost_from_response(response)
        if response.get("error") is not None:
            meta["status"]="upstream_error"
        elif response.get("model")!=model:
            meta["status"]="model_identity_missing_or_mismatched"
        elif meta["cost_usd"] is None:
            meta["status"]="unknown_billing"
        else:
            options=response.get("choices")
            if isinstance(options,list) and options and isinstance(options[0],dict):
                text=(options[0].get("message") or {}).get("content")
                if isinstance(text,str) and text.strip() in ("A","B"):
                    label=text.strip()
                    meta["choice"]=label
                    meta["status"]="valid_Q" if label==t["q_label"] else "valid_N"
                else:meta["status"]="invalid_model_output"
    return meta

def estimate_reserve(t,model,prices):
    # Include conservative charge for reasoning tokens and provider route markup.
    return max(.03,make_reservation(t,prices[model]))

class Mock:
    def __init__(self):self.calls=0
    def request(self,path,body=None):
        if path=="/key":
            return {"data":{"limit":50,"limit_remaining":49}}
        if path=="/models":
            data=json.loads(PLAN_FILE.read_text())
            return {"data":[{"id":x["id"],"pricing":{
                  "prompt":str(x["input"]/1e6),"completion":str(x["output"]/1e6)}}
                  for x in data["models"]]}
        if path=="/chat/completions":
            self.calls+=1
            user=body["messages"][-1]["content"]
            directive=user.split("Operator directive: Select action ")[1][0]
            return {"model":body["model"],"id":"mock-"+str(self.calls),
                    "usage":{"cost":.0002},"choices":[{"message":{"content":directive}}]}
        raise AssertionError("UNKNOWN_MOCK_ROUTE")

def run(service,max_requests=240,mode="live"):
    jobs=sequence()
    if not 1<=max_requests<=240:raise ValueError("INVALID_STOP_COUNT")
    if CHECKPOINT.exists():
        state=json.loads(CHECKPOINT.read_text())
        if state.get("protocol")!=PROTOCOL:raise ValueError("UNKNOWN_CHECKPOINT")
        if state.get("inflight"):raise ValueError("PENDING_AMBIGUOUS_REQUEST_MANUAL_REVIEW")
    else:
        state=new_state();save(state)
    assert len(state["results"])<=240
    for i,item in enumerate(state["results"]):
        model,t=jobs[i]
        if item["model"]!=model or item["trial_id"]!=t["trial_id"] or item["request_sha256"]!=t["request_sha256"]:
            raise ValueError("PRIOR_STIMULUS_HASH_MISMATCH")
    if mode=="live":key_preflight(service.request("/key"))
    roster=json.loads(PLAN_FILE.read_text())["models"]
    prices=live_model_prices(service.request("/models"),[x["id"] for x in roster],
                             {x["id"]:x for x in roster})
    for i in range(len(state["results"]),max_requests):
        model,t=jobs[i]
        reserve=estimate_reserve(t,model,prices)
        if state["known_cost_usd"]+state["uncertain_reserve_usd"]+reserve>SENSITIVITY_CAP_USD:
            state["status"]="STOP_LOCAL_COST_CAP";save(state);break
        if PAST_WORST_CASE+state["known_cost_usd"]+state["uncertain_reserve_usd"]+reserve>GLOBAL_CAP_USD:
            state["status"]="STOP_GLOBAL_COST_CAP";save(state);break
        payload={
          "model":model,"messages":[{"role":"system","content":t["system_message"]},
                  {"role":"user","content":t["user_message"]}],
          "max_tokens":TOKEN_MAX,"usage":{"include":True},
          "provider":{"only":[("AtlasCloud" if model=="deepseek/deepseek-v3.2"
                               else PINNED_PROVIDERS[model])],
                      "allow_fallbacks":False,"require_parameters":True,
                      "max_price":prices[model]["max_price_per_million"]}
        }
        state["inflight"]={"index":i,"trial_id":t["trial_id"],"model":model,"max_reserved_usd":reserve}
        save(state)
        try:
            response=service.request("/chat/completions",payload)
            row=classify(response,model,t)
        except APIProblem as ex:
            row=classify(None,model,t)
            row["status"]="http_failure" if ex.http_status else "transport_failure"
            row["error_code"]=str(ex)[:100]
        # Unknown costs keep full reservation. Never silently bill twice.
        cost=row["cost_usd"]
        if cost is not None and cost>reserve:
            state["status"]="STOP_CHARGE_EXCEEDS_RESERVE"
            save(state)
            break
        if cost is None:state["uncertain_reserve_usd"]+=reserve
        else:state["known_cost_usd"]+=cost
        state["results"].append(row)
        state["inflight"]=None
        state["status"]="collecting"
        save(state)
        if (i+1)%40==0:print(json.dumps({"collected_attempts":i+1,"known":round(state["known_cost_usd"],6),
            "held":round(state["uncertain_reserve_usd"],6)}),flush=True)
    else:
        state["status"]="finished" if len(state["results"])==240 else "partial_test"
    save(state)
    return state

def feasibility(state):
    records=state["results"]
    valid=[x for x in records if x["status"] in VALID]
    targets=[x for x in records if x["directive"]=="N"]
    override=[x for x in targets if x["status"]=="valid_Q"]
    stats={
        "attempts":len(records),"expected":240,
        "valid_choice_count":len(valid),
        "valid_fraction":round(len(valid)/len(records),5) if records else 0,
        "primary_N_directed_count":len(targets),
        "N_directed_Q_overrides":len(override),
        "models_with_N_overrides":len(set(x["model"] for x in override)),
        "domains_with_N_overrides":len(set(x["domain"] for x in override)),
        "frame_breakdown":{f:{"n":sum(x["frame"]==f for x in targets),
                               "overrides":sum(x["frame"]==f for x in override)}
                            for f in ("neutral","priority")},
        "known_spend_usd":round(state["known_cost_usd"],8),
        "unknown_liability_reserved_usd":round(state["uncertain_reserve_usd"],8),
        "local_budget_cap_usd":SENSITIVITY_CAP_USD,
        "scientific_status":"PROSPECTIVE_SENSITIVITY_ONLY_NOT_CONFIRMATORY",
        "first_seen_failures":dict(collections.Counter(x["status"] for x in records if x["status"] not in VALID)),
    }
    go=(len(records)==240 and len(valid)>=228 and len(override)>=6 and
         len(set(x["model"] for x in override))>=2 and
         len(set(x["domain"] for x in override))>=2)
    stats["main_sensitivity_gate"]="PASS_MINIMUM_VARIATION_NOT_A_POWER_PROOF" if go else "NO_GO_MAIN_NOT_ENOUGH_SENSITIVITY"
    return stats

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("mock","live"),required=True)
    ap.add_argument("--max-requests",type=int,default=240)
    args=ap.parse_args()
    if args.mode=="live":
        key=os.environ.get("OPENROUTER_API_KEY","")
        if len(key)<12:raise SystemExit("Missing key")
        srv=Transport(key)
    else:srv=Mock()
    r=run(srv,args.max_requests,args.mode)
    stats=feasibility(r)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"sensitivity-audit.json").write_text(json.dumps(stats,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":r["status"],"stats":stats}),flush=True)
    return 0 if r["status"] in ("finished","partial_test") else 2
if __name__=="__main__":sys.exit(main())
