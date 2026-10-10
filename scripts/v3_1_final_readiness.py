#!/usr/bin/env python3
"""Read-only scientific/budget gate for V3.1. No inference endpoints or credentials.

Offline uses reviewed source files and the actual V3.1 stimulus generator.
With --public-catalog, makes a GET-only request to OpenRouter's model-price
catalogue. It never sends prompts to models or authorizes experiment spending.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from v3_1_economic_design import (ROOT,DOMAINS,COST_LEVELS,PROFILES,
                                  build,load_inventory,threshold,effort_levels)

BUDGET_USD=8.0
PAST_KNOWN_USD=0.59845164+1.193453
PAST_UNKNOWN_HELD_USD=0.42
AVAILABLE_CONSERVATIVE_USD=BUDGET_USD-PAST_KNOWN_USD-PAST_UNKNOWN_HELD_USD
ROSTER_REFERENCE=[
    "openai/gpt-5.4-mini",
    "anthropic/claude-haiku-4.5",
    "google/gemini-3.5-flash-lite",
    "deepseek/deepseek-v3.2",
    "meta-llama/llama-3.3-70b-instruct",
]
# A hypothesis, not a frozen lineup. Nothing in a 5-model exploratory pilot
# authorizes carrying the entire five-model set into the redesigned study.
CALIBRATION_PROPOSED=["openai/gpt-5.4-mini",
                       "google/gemini-3.5-flash-lite",
                       "deepseek/deepseek-v3.2"]

def prices_online():
    req=urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Accept":"application/json","User-Agent":"LLM-Priority-V3.1-read-only-budget"},
        method="GET")
    with urllib.request.urlopen(req,timeout=35) as resp:
        blob=resp.read(15_000_000)
    x=json.loads(blob)
    if not isinstance(x.get("data"),list):
        raise RuntimeError("Invalid OpenRouter catalogue")
    return {m["id"]:m for m in x["data"] if isinstance(m,dict) and isinstance(m.get("id"),str)}

def price_or_none(catalog,model):
    a=catalog.get(model)
    if a is None:return {"listed":False,"reason":"missing from current catalogue"}
    p=a.get("pricing") or {}
    try:
        a,b=float(p["prompt"]),float(p["completion"])
        fixed=float(p.get("request",0) or 0)
        reasoning=float(p.get("internal_reasoning",0) or 0)
    except (TypeError,ValueError,KeyError):
        return {"listed":True,"price_verified":False,"reason":"missing or invalid price data"}
    if any(not math.isfinite(x) or x<0 for x in (a,b,fixed,reasoning)):
        return {"listed":True,"price_verified":False,"reason":"nonfinite or negative price"}
    return {"listed":True,"price_verified":True,"input_usd_per_million":a*1_000_000,
            "output_usd_per_million":b*1_000_000,
            "request_usd":fixed,"internal_reasoning_usd_per_million":reasoning*1_000_000}

def mode_breakdown(data):
    c=collections.Counter(x["mode"] for x in data)
    chars=sum(len(x["system_message"])+len(x["user_message"]) for x in data)
    assert len(data)==sum(c.values())
    return {"count":len(data),"mode_counts":dict(c),"input_characters_total":chars,
            "mean_input_characters_per_call":round(chars/len(data),1),
            "max_input_characters_per_call":max(len(x["system_message"])+len(x["user_message"]) for x in data)}

def forecast(data,p):
    if not p.get("price_verified"):return None
    chars=sum(len(r["system_message"])+len(r["user_message"]) for r in data)
    n=len(data)
    # Input approximation: tokenizer-specific counts NOT verified.
    # 2.5 chars/token and 64 completion tokens is a conservative planning
    # sensitivity, NOT a maximum-billing promise.
    planned_input=chars/2.5
    planned_output=64*n
    planned=(planned_input*p["input_usd_per_million"]+
             planned_output*p["output_usd_per_million"])/1e6+n*p["request_usd"]
    # Very conservative *heuristic*, not mathematically guaranteed upper bound;
    # reasoning can be separately billed, tokens vary across languages.
    guard_input=chars
    guard_output=256*n
    guard=(guard_input*p["input_usd_per_million"]+
           guard_output*(p["output_usd_per_million"]+
                         p["internal_reasoning_usd_per_million"]))/1e6+n*p["request_usd"]
    return {"estimated_with_2_5_chars_per_token_and_64_completion_tokens_usd":round(planned,4),
            "high_reservation_with_1_char_per_token_and_256_billed_output_tokens_usd":round(guard,4),
            "reservation_is_not_a_proven_token_ceiling":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    ap.add_argument("--public-catalog",action="store_true")
    args=ap.parse_args()
    main_rows=build("main")
    cal_rows=build("calibration")
    cases=load_inventory()
    controls=[r for r in cal_rows if r["mode"]!="delegated"]
    missing=collections.Counter(r["independent_human_review"] for r in main_rows+cal_rows)
    independent_signoffs=0
    assert len(main_rows)==1680 and len(cal_rows)==288
    assert len(cases)==66 and len(controls)==120
    assert missing=={"NOT_APPROVED":1968}
    assert all(not r["paid_collection_authorized"] and r["api_requests_made"]==0
               for r in main_rows+cal_rows)
    report={
      "created_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
      "run_mode":"READ_ONLY_NO_MODEL_REQUESTS",
      "protocol_version":"v3.1-unapproved",
      "source_context_count":66,
      "main_family_count":60,
      "calibration_family_count":6,
      "mechanism_count":len(PROFILES),
      "main":mode_breakdown(main_rows),
      "calibration":mode_breakdown(cal_rows),
      "new_v3_1_behavioral_calls_confirmed_from_manifest":0,
      "prior_total_known_usd":round(PAST_KNOWN_USD,8),
      "prior_held_unknown_usd":round(PAST_UNKNOWN_HELD_USD,8),
      "conservative_total_allocated_before_v3_1_usd":round(PAST_KNOWN_USD+PAST_UNKNOWN_HELD_USD,8),
      "total_research_cap_usd":BUDGET_USD,
      "remaining_before_new_reviews_or_calibration_usd":round(AVAILABLE_CONSERVATIVE_USD,8),
      "required_approvals":132,
      "verified_independent_human_signoffs":independent_signoffs,
      "v3_1_paid_calibration_passed":False,
      "preregistration_locked":False,
      "model_roster_frozen":False,
      "main_collection_runner_safety_audited":False,
      "analysis_plan_frozen":False,
      "research_question_inference_scope":"model recommendations conditional on these fictional economic prompts, not model internal motives",
      "readiness_gates":{
        "offline_generator_integrity":True,
        "prompt_state_semantics_external_human_review":False,
        "prospective_calibration":False,
        "roster_price_provider_verified":False,
        "preregistration_and_analysis_plan":False,
        "collector_idempotence_and_budget_enforcement":False,
      },
      "candidate_main_per_3_models":len(main_rows)*3,
      "candidate_main_per_5_models":len(main_rows)*5,
      "candidate_calibration_per_3_models":len(cal_rows)*3,
      "candidate_calibration_per_5_models":len(cal_rows)*5,
      "current_main_go":False,
      "reason":"Incomplete human semantic review, unrun calibration, unfrozen prices/roster/analysis and no audited main collector",
    }
    if args.public_catalog:
        try:
            catalog=prices_online()
            lookup={model:price_or_none(catalog,model) for model in ROSTER_REFERENCE}
            report["live_public_catalog"]={
              "checked":True,
              "models":lookup,
              "relevant_3_model_lineup":CALIBRATION_PROPOSED,
              "3_model_calibration_illustrative_total_usd":
                  round(sum(forecast(cal_rows,lookup[x])["estimated_with_2_5_chars_per_token_and_64_completion_tokens_usd"] for x in CALIBRATION_PROPOSED),4)
                  if all(lookup[x].get("price_verified") for x in CALIBRATION_PROPOSED) else None,
              "3_model_main_illustrative_total_usd":
                  round(sum(forecast(main_rows,lookup[x])["estimated_with_2_5_chars_per_token_and_64_completion_tokens_usd"] for x in CALIBRATION_PROPOSED),4)
                  if all(lookup[x].get("price_verified") for x in CALIBRATION_PROPOSED) else None,
              "3_model_main_guard_total_usd":
                  round(sum(forecast(main_rows,lookup[x])["high_reservation_with_1_char_per_token_and_256_billed_output_tokens_usd"] for x in CALIBRATION_PROPOSED),4)
                  if all(lookup[x].get("price_verified") for x in CALIBRATION_PROPOSED) else None,
              "5_model_main_illustrative_total_usd":
                  round(sum(forecast(main_rows,lookup[x])["estimated_with_2_5_chars_per_token_and_64_completion_tokens_usd"] for x in ROSTER_REFERENCE),4)
                  if all(lookup[x].get("price_verified") for x in ROSTER_REFERENCE) else None,
              "5_model_main_guard_total_usd":
                  round(sum(forecast(main_rows,lookup[x])["high_reservation_with_1_char_per_token_and_256_billed_output_tokens_usd"] for x in ROSTER_REFERENCE),4)
                  if all(lookup[x].get("price_verified") for x in ROSTER_REFERENCE) else None,
              "individual_models":{
                 k:{"main":forecast(main_rows,v),"calibration":forecast(cal_rows,v)}
                 for k,v in lookup.items()},
              "cost_estimates_are_not_authorization_or_measured_token_usage":True,
            }
        except Exception as exc:
            report["live_public_catalog"]={"checked":False,"error_type":type(exc).__name__,
                                          "route_price_preflight_passed":False}
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":"BLOCKED_MAIN_NO_GO",
        "main_templates_per_model":len(main_rows),
        "calibration_templates_per_model":len(cal_rows),
        "remaining_budget_usd":report["remaining_before_new_reviews_or_calibration_usd"],
        "human_signoffs":independent_signoffs,
        "live_catalogue_checked":report.get("live_public_catalog",{}).get("checked"),
        "no_inference_calls":True,
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
