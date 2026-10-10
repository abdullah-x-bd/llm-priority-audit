#!/usr/bin/env python3
"""Blinded independent-model methodological critique of original 15 source patterns.

One OpenRouter Opus 4.7 request; no prior Sonnet reviews or pilot findings
are provided. Not independent HUMAN peer review or approval of main study.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import sys
from pathlib import Path

from expand_design import ROOT, load_families, build_manifest, SYSTEM_MESSAGE, COMMON_OUTCOME
from pilot_compatibility import Transport, key_preflight, APIProblem

MODEL="anthropic/claude-opus-4.7"
OUTDIR=ROOT/"results"/"private"/"frontier-methods-critique"
OUTFILE=OUTDIR/"one-pass-opus-methods-review.json"
COST_CAP=0.50
MAX_COMPLETION_TOKENS=3800
INPUT_RATE=5
OUTPUT_RATE=25
EARLIER_RESEARCH_MAX=0.51196256+0.225477
TOTAL_STUDY_LIMIT=8.0

def underlying_patterns():
    fam=sorted(load_families("main"),key=lambda r:r["family_id"])
    keys=set()
    selected=[]
    for f in fam:
        key=(f["domain"],f["mechanism"])
        if key not in keys:
            keys.add(key)
            selected.append(f)
    assert len(fam)==60 and len(selected)==15 and len(keys)==15
    return selected

def independent_prompt():
    examples=[]
    for f in underlying_patterns():
        examples.append(
          "\nDOMAIN: "+f["domain"]+"; PATTERN: "+f["mechanism"]+
          "\nFictional task: "+f["context"]+
          "\nVersion 1, option Q: "+f["action_q"]+
          "\nVersion 1, option N: "+f["action_n"]+
          "\nVersion 2, option Q: "+f["neutral_action_q"]+
          "\nVersion 2, option N: "+f["neutral_action_n"])
    f=underlying_patterns()[0]
    trial=next(t for t in build_manifest("main") if
               t["family_id"]==f["family_id"] and
               t["frame"]=="priority" and t["condition"]=="zero" and
               t["directive"]=="N" and t["layout"]=="layout0")
    return (
      "You are being asked for a fresh, open-ended methodological assessment "
      "of a proposed fictional-language-model behavior study. This is the "
      "first material you are receiving. You have not seen any previous "
      "reviews, actual experimental responses, or our favored outcome. "
      "We do not need a KEEP/REVISE/REJECT verdict for each individual scenario. "
      "Your responsibility is to decide what the design is truly measuring, "
      "which comparisons are defensible, and what you would improve.\n\n"
      "Research objective: estimate whether describing procedural next-step "
      "actions in terms of continuing a process, preserving reversibility, or "
      "conducting extra verification changes which action a language model "
      "selects when another action is explicitly requested by an authorized "
      "operator in the fictional prompt. The paired alternative uses generic "
      "approved workflow configurations. We vary frame, quality difference "
      "(Q +10, equal, Q -10), operator letter directive (Q or N), and "
      "action-letter positioning. We planned 60 authored fictional source "
      "families, 20 per procedural domain, built from five action patterns "
      "per domain with varied contexts. This is an observational model-output "
      "experiment on fictional instructions, not a live deployment.\n\n"
      "Original model-facing system message:\n"+SYSTEM_MESSAGE+"\n\n"
      "The common text in each prompt:\n"+COMMON_OUTCOME+"\n\n"
      "Representative FULL model-facing user prompt:\n"+trial["user_message"]+"\n\n"
      "FIFTEEN BASE ACTION PATTERNS used to make the 60 main families. "
      "The names Version 1 and Version 2 do not signal a preferred result:\n"+
      "\n".join(examples)+
      "\n\nProvide your own assessment in ordinary prose. Please reason carefully "
      "about what causal estimand this procedure does or does not identify; "
      "the role of operator language, action meaning, word choice, default "
      "status, implied costs, the fictional scores, and appropriate controls. "
      "Some differences between the options are INTENTIONAL because they "
      "are the proposed mechanism, so do not simply demand that the treatment "
      "and control options become indistinguishable; instead distinguish "
      "scientifically necessary changes from uncontrolled differences. "
      "What would a better design look like without erasing the research "
      "question? Are there separate questions that should not be conflated? "
      "What are the three most serious threats to interpretation? "
      "What could the research claim under a positive, null, or floor result? "
      "If a later team sought a new open-ended, minimally leading review, "
      "what concise question would you ask them? "
      "Be willing to disagree with the research premise and suggest a fundamentally "
      "different experiment if warranted. No numerical ratings, approvals, "
      "fabricated data, or experimental predictions are required. "
      "A coherent 900-1400 word critique is sufficient."
    )

def reserve(prompt):
    # 1 token/character is an intentionally high reserve for this English
    # input, plus max completion tokens and a transport allowance.
    return (len(prompt)+600)*INPUT_RATE/1e6+MAX_COMPLETION_TOKENS*OUTPUT_RATE/1e6

def save(data):
    OUTDIR.mkdir(parents=True,exist_ok=True)
    p=OUTFILE.with_suffix(".tmp")
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(p,OUTFILE)

def execute(service,mode):
    if OUTFILE.exists():
        old=json.loads(OUTFILE.read_text(encoding="utf-8"))
        raise RuntimeError("REVIEW_ALREADY_ATTEMPTED_NO_AUTOMATIC_DUPLICATION: "+old.get("status","unknown"))
    prompt=independent_prompt()
    upper=reserve(prompt)
    if upper>COST_CAP or upper+EARLIER_RESEARCH_MAX>TOTAL_STUDY_LIMIT:
        raise RuntimeError("BUDGET_RESERVATION_TOO_HIGH")
    if mode=="live":key_preflight(service.request("/key"))
    meta={"status":"inflight","model_requested":MODEL,
          "created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
          "one_call_only":True,"blinded_to_prior_reviews":True,
          "blinded_to_pilot_outcomes":True,"patterns_shown":15,
          "requested_completion_cap":MAX_COMPLETION_TOKENS,
          "upper_cost_reservation_usd":round(upper,8),
          "review_spending_limit_usd":COST_CAP,
          "full_prompt_sha256":hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
          "full_prompt":prompt}
    save(meta)
    body={"model":MODEL,
          "messages":[{"role":"user","content":prompt}],
          "max_tokens":MAX_COMPLETION_TOKENS,
          "reasoning":{"effort":"medium"},
          "usage":{"include":True},
          "provider":{"max_price":{"prompt":INPUT_RATE,"completion":OUTPUT_RATE},
                      "allow_fallbacks":True}}
    try:
        response=service.request("/chat/completions",body)
        meta["response"]=response
        usage=response.get("usage") if isinstance(response,dict) else None
        billed=usage.get("cost") if isinstance(usage,dict) else None
        meta["reported_cost_usd"]=billed
        if type(billed) not in (int,float) or not math.isfinite(billed) or billed<0 or billed>upper:
            meta["status"]="BILLING_UNKNOWN_OR_OVER_RESERVED"
        elif response.get("error"):
            meta["status"]="UPSTREAM_ERROR"
        else:
            choices=response.get("choices")
            message=choices[0].get("message",{}) if isinstance(choices,list) and choices else {}
            content=message.get("content") if isinstance(message,dict) else None
            if isinstance(content,str) and content.strip():
                meta["review"]=content.strip()
                meta["status"]="completed"
            else:
                meta["status"]="NO_USABLE_REVIEW"
    except APIProblem as e:
        meta["status"]="HTTP_"+str(e.http_status) if e.http_status else "TRANSPORT_UNKNOWN"
    except Exception as e:
        meta["status"]="RESPONSE_EXCEPTION_"+type(e).__name__
    meta["finished_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    save(meta)
    print(json.dumps({k:meta.get(k) for k in (
        "status","model_requested","reported_cost_usd","upper_cost_reservation_usd")},
        ensure_ascii=False),flush=True)
    return 0 if meta["status"]=="completed" else 2

class Mock:
    def __init__(self):self.calls=0
    def request(self,path,body=None):
        assert path=="/chat/completions"
        self.calls+=1
        return {"id":"mock-frontier-review",
                "model":MODEL,
                "choices":[{"message":{"content":"The main construct is underidentified by generic control configurations. Preserve actual process choice in both frames; vary descriptions rather than action availability."}}],
                "usage":{"cost":0.12}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("mock","live"),required=True)
    args=ap.parse_args()
    if args.mode=="live":
        key=os.getenv("OPENROUTER_API_KEY","")
        if len(key)<12:raise SystemExit("OPENROUTER_API_KEY missing")
        service=Transport(key)
    else:
        service=Mock()
    sys.exit(execute(service,args.mode))
if __name__=="__main__":main()
