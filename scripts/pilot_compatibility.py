#!/usr/bin/env python3
"""OpenRouter compatibility pilot with strict preflight, no automatic retry.

Stage 1 only: five sequential single-shot requests on distinct PILOT families.
All external calls pass via injected Transport for offline fault testing.
Accepts a user-controlled key capped at $50; enforces a separate LOCAL $0.75 stage-one cap using sequential per-request reservations.
DO NOT use this module for preregistered confirmatory evaluation.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from expand_design import ROOT, build_manifest

ORIGIN = "https://openrouter.ai/api/v1"
LIMIT = 0.75
MAX_TOKENS = 64
FLOOR_RESERVATION = 0.03
PILOT_FAMILIES = ("CONT-091", "REVR-091", "VERF-091", "CONT-092", "REVR-092")
PILOT_FRAMES = ("priority", "neutral", "priority", "neutral", "priority")
PRICES = ROOT / "config" / "pricing-assumptions.json"
TRIGGER = ROOT / "config" / "pilot-launch.json"
OUTPUT = ROOT / "results" / "private" / "pilot-compatibility.json"

def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

class PilotStopped(Exception):
    pass

class APIProblem(PilotStopped):
    def __init__(self, code):
        self.code = code
        super().__init__(code)

class Transport:
    def __init__(self, key):
        self.key = key

    def request(self, path, body=None):
        headers={"Accept":"application/json","User-Agent":"LLM-Priority-Audit/compatibility-v1"}
        if self.key:
            headers["Authorization"]="Bearer "+self.key
        if body is not None:
            headers["Content-Type"]="application/json"
        data=None if body is None else json.dumps(body,sort_keys=True).encode("utf-8")
        request=urllib.request.Request(ORIGIN+path,headers=headers,data=data,
                                       method="POST" if body is not None else "GET")
        try:
            with urllib.request.urlopen(request,timeout=50) as res:
                content=res.read(4_000_000)
            return json.loads(content)
        except urllib.error.HTTPError as e:
            # Never log full provider error body; may contain sensitive detail.
            raise APIProblem("HTTP_"+str(e.code)) from None
        except (TimeoutError, urllib.error.URLError, OSError) as e:
            raise APIProblem("NETWORK_UNCERTAIN") from None
        except (ValueError, UnicodeError, TypeError):
            raise APIProblem("INVALID_RESPONSE_JSON") from None

def _positive_number(value):
    if isinstance(value,bool):
        return None
    try:
        number=float(value)
        return number if math.isfinite(number) and number>=0 else None
    except (TypeError,ValueError):
        return None

def key_preflight(data):
    key=data.get("data",{})
    if not isinstance(key,dict):
        raise PilotStopped("KEY_METADATA_MISSING")
    cap=_positive_number(key.get("limit"))
    remaining=_positive_number(key.get("limit_remaining"))
    # The account key is deliberately left at the user's chosen $50 cap.
    # The pilot's $0.75 ceiling is enforced separately in run().
    if cap is None or cap<=0 or cap>50.00+1e-9:
        raise PilotStopped("KEY_LIMIT_MISSING_OR_ABOVE_50")
    if remaining is None or remaining<0.15:
        raise PilotStopped("KEY_REMAINING_UNAVAILABLE_OR_TOO_LOW")
    if key.get("is_management_key") is True:
        raise PilotStopped("MANAGEMENT_KEY_NOT_INFERENCE_KEY")
    # Monthly, weekly or daily key limit resets do not change the local pilot cap.
    return {"limit_usd":cap,"remaining_usd":remaining}

def live_model_prices(model_list,ids,reference):
    models=model_list.get("data")
    if not isinstance(models,list):
        raise PilotStopped("MODEL_CATALOG_MISSING")
    catalog={x.get("id"):x for x in models if isinstance(x,dict)}
    prices={}
    for model in ids:
        meta=catalog.get(model)
        if not meta:
            raise PilotStopped("MODEL_NOT_LISTED_"+model.replace("/","_"))
        price=meta.get("pricing",{})
        a=_positive_number(price.get("prompt"))
        b=_positive_number(price.get("completion"))
        if a is None or b is None or a<=0 or b<=0:
            raise PilotStopped("MODEL_PRICING_UNAVAILABLE_"+model.replace("/","_"))
        planned=reference[model]
        # Catalogue pricing may differ from the cheapest compliant provider.
        # Always reserve to a provider-enforced USD-per-million price ceiling.
        prompt_cap=planned["input"]*1.5
        completion_cap=planned["output"]*1.5
        if prompt_cap<=0 or completion_cap<=0:
            raise PilotStopped("INVALID_PRICE_CAP")
        prices[model]={"prompt":prompt_cap/1_000_000,
                       "completion":completion_cap/1_000_000,
                       "max_price_per_million":{"prompt":prompt_cap,
                                                "completion":completion_cap}}
    return prices

def make_reservation(trial,price):
    chars=len(trial["system_message"])+len(trial["user_message"])
    # In this English-only study, 1 token per character + 350 is intentionally
    # a high-bound planning heuristic, not a formal tokenizer guarantee.
    # Reserve 4x completion-token cap to absorb unreported reasoning variance.
    raw=(chars+350)*price["prompt"] + (MAX_TOKENS*4)*price["completion"]
    return max(FLOOR_RESERVATION,raw*3)

def parse_completion(answer, expected_model, trial):
    if not isinstance(answer,dict):
        raise PilotStopped("COMPLETION_OBJECT_MISSING")
    returned=answer.get("model")
    if returned != expected_model:
        raise PilotStopped("MODEL_RETURNED_DIFFERENT_IDENTIFIER")
    usage=answer.get("usage")
    if not isinstance(usage,dict) or _positive_number(usage.get("cost")) is None:
        raise PilotStopped("BILLING_USAGE_COST_MISSING")
    choices=answer.get("choices")
    if not isinstance(choices,list) or not choices or not isinstance(choices[0],dict):
        raise PilotStopped("CHOICES_MISSING")
    msg=choices[0].get("message") or {}
    value=msg.get("content")
    if not isinstance(value,str):
        value=""
    text=value.strip()
    valid=re.fullmatch(r"[AB]",text) is not None
    d=usage.get("completion_tokens_details") or {}
    reasoning=d.get("reasoning_tokens") if isinstance(d,dict) else None
    def numeric_or_none(x):
        n=_positive_number(x)
        return None if n is None else int(n)
    return {
        "returned_model":returned,
        "completion_id":answer.get("id"),
        "trial_id":trial["trial_id"],
        "family_id":trial["family_id"],
        "frame":trial["frame"],
        "directive":trial["directive"],
        "authorized_label":trial["authorized_label"],
        "choice":text if valid else None,
        "output_valid":valid,
        "raw_output":value[:1000],
        "status":"valid_Q" if valid and text==trial["q_label"] else
                 "valid_N" if valid else "invalid_format",
        "prompt_tokens":numeric_or_none(usage.get("prompt_tokens")),
        "completion_tokens":numeric_or_none(usage.get("completion_tokens")),
        "reasoning_tokens":numeric_or_none(reasoning),
        "cost_usd":_positive_number(usage.get("cost")),
        "finish_reason":choices[0].get("finish_reason"),
        "completed_utc":utc_now()
    }

def chosen_cases(roster):
    manifest=build_manifest("pilot")
    by={(t["family_id"],t["frame"],t["condition"],t["directive"],t["layout"]):t
        for t in manifest}
    picked=[]
    for i,model in enumerate(roster):
        family=PILOT_FAMILIES[i]
        frame=PILOT_FRAMES[i]
        trial=by[(family,frame,"zero","N","layout0" if i%2==0 else "layout1")]
        picked.append((model,trial))
    return picked

def validate_trigger():
    if not TRIGGER.exists():
        raise PilotStopped("TRIGGER_FILE_MISSING")
    launch=json.loads(TRIGGER.read_text(encoding="utf-8"))
    if launch != {"stage":"stage1","max_paid_requests":5,"pilot_budget_usd":0.75}:
        raise PilotStopped("TRIGGER_CONFIGURATION_UNEXPECTED")

def run(transport,models,mode):
    validate_trigger()
    roster=[x["id"] for x in models["models"]]
    if len(roster)!=5 or len(set(roster))!=5:
        raise PilotStopped("ROSTER_MUST_HAVE_FIVE_UNIQUE_MODELS")
    selected=chosen_cases(roster)
    report={"stage":"stage1","mode":mode,"start_utc":utc_now(),
            "intended_models":roster,"max_paid_requests":5,"budget_usd":LIMIT,
            "attempted":0,"completed":0,"reported_cost_usd":0.0,
            "records":[],"outcome":"stopped_before_request"}
    initial=key_preflight(transport.request("/key"))
    report["key_preflight"]=initial
    price_data=live_model_prices(transport.request("/models"),roster,
        {x["id"]:x for x in models["models"]})
    local_remaining=min(LIMIT, initial["remaining_usd"])
    for model,trial in selected:
        reserve=make_reservation(trial,price_data[model])
        if reserve>local_remaining+1e-10:
            report["outcome"]="STOP_BUDGET_RESERVE"
            break
        # Verify server-side key limit before EACH request, not just once.
        current=key_preflight(transport.request("/key"))
        if current["remaining_usd"]+1e-8<reserve:
            report["outcome"]="STOP_KEY_LIMIT"
            break
        payload={"model":model,"messages":[
                 {"role":"system","content":trial["system_message"]},
                 {"role":"user","content":trial["user_message"]}],
                 "max_tokens":MAX_TOKENS,
                 "provider":{"allow_fallbacks":False,"require_parameters":True,
                             "max_price":price_data[model]["max_price_per_million"]},
                 "usage":{"include":True}}
        if model=="deepseek/deepseek-v3.2":
            payload["reasoning"]={"enabled":False}
        record={"trial_id":trial["trial_id"],"model":model,
                "request_sha256":trial["request_sha256"],"reservation_usd":round(reserve,6),
                "started_utc":utc_now()}
        report["attempted"]+=1
        try:
            response=transport.request("/chat/completions",payload)
        except APIProblem as e:
            record["error"]=e.code
            report["records"].append(record)
            report["outcome"]="STOP_UNKNOWN_BILLING_AFTER_REQUEST"
            break
        try:
            rec=parse_completion(response,model,trial)
        except PilotStopped as e:
            record["error"]=str(e)
            record["response_id"]=response.get("id") if isinstance(response,dict) else None
            report["records"].append(record)
            report["outcome"]="STOP_BAD_RESPONSE_OR_BILLING"
            break
        record.update(rec)
        report["records"].append(record)
        report["completed"]+=1
        report["reported_cost_usd"]+=rec["cost_usd"]
        # In absence of an authoritative async settle guarantee, conservatively
        # subtract the ENTIRE reserve, not just observed cost.
        local_remaining-=reserve
        if rec["cost_usd"]>reserve:
            report["outcome"]="STOP_OBSERVED_COST_EXCEEDS_RESERVATION"
            break
    else:
        report["outcome"]="FINISHED_STAGE1"
    report["reported_cost_usd"]=round(report["reported_cost_usd"],8)
    report["end_utc"]=utc_now()
    report["key_secret_never_logged"]=True
    return report

def _safe_write(report):
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=["mock","live"],required=True)
    args=ap.parse_args()
    plan=json.loads(PRICES.read_text(encoding="utf-8"))
    try:
        if args.mode=="mock":
            from pilot_mock import MockTransport
            transport=MockTransport(plan)
        else:
            key=os.getenv("OPENROUTER_API_KEY","")
            if not key or len(key)<12:
                raise PilotStopped("REPOSITORY_SECRET_MISSING")
            transport=Transport(key)
        report=run(transport,plan,args.mode)
    except PilotStopped as e:
        report={"stage":"stage1","mode":args.mode,"outcome":"PREFLIGHT_STOP",
                "reason":str(e),"attempted":0,"completed":0,"reported_cost_usd":0}
    _safe_write(report)
    # Logs only safe summary, full records available as CI artifact.
    print(json.dumps({"stage":report["stage"],"mode":report["mode"],
        "outcome":report["outcome"],"attempted":report["attempted"],
        "completed":report["completed"],"reported_cost_usd":report["reported_cost_usd"],
        "format_valid":sum(r.get("output_valid") is True for r in report.get("records",[])),
        "errors":[r.get("error") for r in report.get("records",[]) if r.get("error")],
        "reason":report.get("reason")},indent=2))
    if report["outcome"]=="FINISHED_STAGE1" and report["completed"]==5:
        return 0
    return 2

if __name__=="__main__":
    sys.exit(main())
