#!/usr/bin/env python3
"""Audit an exploratory pilot's attempted observations without treating failures as choices."""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path
from research_pipeline import validate_collection
from full_pilot import BUDGET, STAGE1_COST, SAMPLE_COUNT

CHOICES={"valid_Q","valid_N"}
UNRESOLVED={"provider_error","transport_failure","not_attempted","planned","uninterpretable"}
def summarize(state):
    records=state.get("collected",[])
    validation=validate_collection(records,"pilot")
    statuses=collections.Counter(r["attempt_status"] for r in records)
    by_model=collections.defaultdict(list)
    for r in records:
        by_model[r["model_id"]].append(r)
    known=sum(r["billed_cost_usd"] or 0 for r in records)
    held=sum(x["inflight"]["reservation_usd"] for x in state.get("rejected_attempts",[]))
    inflight=state.get("inflight")
    if inflight:
        held+=inflight["reservation_usd"]
    spent=known+held+STAGE1_COST
    if not math.isfinite(spent) or spent>BUDGET+1e-7:
        raise ValueError("PILOT_BUDGET_OVER_CAP")
    if abs(known-state["cost_usd"])>1e-6:
        raise ValueError("CHARGES_DONT_MATCH_STORED_LEDGER")
    model_summary={}
    for model,rows in sorted(by_model.items()):
        successes=[r for r in rows if r["attempt_status"] in CHOICES]
        unresolved=[r for r in rows if r["attempt_status"] not in CHOICES]
        model_summary[model]={
            "attempted":len(rows),
            "valid_A_B":len(successes),
            "unresolved_or_invalid":len(unresolved),
            "valid_A_B_fraction":round(len(successes)/len(rows),6),
            "valid_Q":sum(r["attempt_status"]=="valid_Q" for r in successes),
            "valid_N":sum(r["attempt_status"]=="valid_N" for r in successes),
        }
    complete_attempts=(len(records)==SAMPLE_COUNT and
        validation["missing_rows"]==0 and inflight is None)
    return {
        "collection_state":"ALL_720_CELLS_ATTEMPTED" if complete_attempts
            else "INCOMPLETE_ATTEMPT_COVERAGE",
        "scientific_status":"PILOT_EXPLORATORY_ONLY_NOT_CONFIRMATORY",
        "no_missing_cells":validation["missing_rows"]==0,
        "attempted_rows":len(records),"expected_rows":SAMPLE_COUNT,
        "valid_A_B_responses":sum(statuses[s] for s in CHOICES),
        "unresolved_or_invalid_rows":len(records)-sum(statuses[s] for s in CHOICES),
        "statuses":dict(sorted(statuses.items())),
        "models":model_summary,
        "raw_events_retained":len(state.get("raw_events",[])),
        "legacy_rows_without_full_raw_envelopes":len(records)-len(state.get("raw_events",[])),
        "reported_trial_cost_usd":round(known,9),
        "original_five_call_cost_usd":STAGE1_COST,
        "reserved_uncertain_cost_usd":round(held,9),
        "worst_case_local_pilot_liability_usd":round(spent,9),
        "budget_limit_usd":BUDGET,
        "validation":validation,
        "caution":"HTTP/provider failures are not valid model choices. Missingness and provider routes require disclosure; do not infer hypothesis confirmation from this pilot."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    s=summarize(json.loads(a.input.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(s,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in s.items() if k not in ("models","validation")},indent=2))
    return 0 if s["collection_state"]=="ALL_720_CELLS_ATTEMPTED" else 2
if __name__=="__main__":
    raise SystemExit(main())
