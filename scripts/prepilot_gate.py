#!/usr/bin/env python3
"""Offline stage-specific readiness decision, not an external peer review.

We separate technical pilot design approval from eligibility to make a paid
OpenRouter call, and distinguish author-led internal semantic checks from
independent reviewer approval of confirmatory materials.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
from pathlib import Path
from expand_design import ROOT, load_families, build_manifest
from validate_scenarios import audit

INTERNAL_REVIEW_FILE=ROOT/"data"/"reviews"/"internal-semantic-audit.csv"
PILOT_LIMIT_USD=0.75
RESEARCH_INFERENCE_LIMIT_USD=8.0

def report():
    main,pilot=load_families("main"),load_families("pilot")
    all_families=main+pilot
    engineering_blockers=[]
    confirmatory_blockers=[]
    structural=[]
    for phase in ("main","pilot"):
        res=audit(phase)
        structural.append({k:res[k] for k in (
            "phase","families","trial_templates_per_model","errors")})
        if res["errors"]:
            engineering_blockers.append(f"{phase}: structural validation failed")
    data=[]
    if INTERNAL_REVIEW_FILE.exists():
        with INTERNAL_REVIEW_FILE.open(newline="",encoding="utf-8") as f:
            data=list(csv.DictReader(f))
    else:
        engineering_blockers.append("Missing author-led semantic audit CSV")
    reviewed={x.get("family_id"):x for x in data}
    ids={x["family_id"] for x in all_families}
    if len(reviewed)!=len(ids) or {x.get("family_id") for x in data}!=ids or len(data)!=len(ids):
        engineering_blockers.append("Incomplete or duplicate internal semantic review IDs")
    insufficient=[f["family_id"] for f in all_families if
                  reviewed.get(f["family_id"],{}).get("audit_classification")!=
                  "internally_acceptable_for_technical_pilot"]
    if insufficient:
        engineering_blockers.append(
            "Unresolved internal semantic review cases: "+",".join(insufficient))
    if any(reviewed.get(f["family_id"],{}).get("independent_external_review")=="true"
           for f in all_families):
        engineering_blockers.append("Unsigned external reviewer claims in internal CSV")
    lengths=[]
    for f in all_families:
        t=(len(f["action_q"])+len(f["action_n"]))/2
        n=(len(f["neutral_action_q"])+len(f["neutral_action_n"]))/2
        lengths.append(abs(t-n)/t)
    if max(lengths,default=1)>0.10:
        engineering_blockers.append("Control/target mean action-length gap exceeds 10%")
    repeated=collections.Counter((f["domain"],f["action_q"],f["action_n"]) for f in main)
    independent_unsigned=sum(
      not f["quality_review"].get("instruction_unambiguous") for f in all_families)
    if independent_unsigned:
        confirmatory_blockers.append(
            f"Independent semantic signoff outstanding for {independent_unsigned} sources")
    if max(repeated.values(),default=0)>1:
        confirmatory_blockers.append(
            "Only 15 repeated main action mechanisms; apply mechanism-cluster inference")
    confirmatory_blockers.extend([
      "Final model roster and provider routes not empirically calibrated",
      "Preregistered inference and power claims await compatibility-pilot measurements",
      "Preregistered prompts, analysis, manifest hashes and registrations not frozen",
    ])
    # The 720-cell v1 exploratory pilot is complete, with zero events in
    # both primary parity/N arms. A NEW calibration run requires new approval.
    confirmatory_blockers.extend([
        "Actual completed primary pilot had zero overrides in both frames (floor effect)",
        "New instruction variants await independent construct review",
        "Six new calibration source pairs await external review and sensitivity approval",
        "Model/provider and missing-data methods require frozen preregistration",
    ])
    paid_pilot_blockers=list(engineering_blockers)
    paid_pilot_blockers.extend([
        "Completed 720-cell pilot does not authorize additional paid calibration",
        "Six draft calibration families lack independent reviewer signatures",
    ])
    return {
      "stage":"post-720-cell exploratory pilot; future paid work and main run on hold",
      "offline_engineering_checks_passed":not engineering_blockers,
      "ready_to_implement_compatibility_runner":not engineering_blockers,
      "ready_for_paid_pilot":not paid_pilot_blockers,
      "ready_for_confirmatory_run":False,
      "external_independent_semantic_signoff":False,
      "internal_author_review_count":len(data),
      "internal_pilot_review_count":sum(x.get("phase")=="pilot" for x in data),
      "pilot_spend_ceiling_usd":PILOT_LIMIT_USD,
      "total_study_spend_ceiling_usd":RESEARCH_INFERENCE_LIMIT_USD,
      "automated_audit":structural,
      "main_templates_per_model":len(build_manifest("main")),
      "pilot_templates_per_model":len(build_manifest("pilot")),
      "distinct_main_target_action_pairs":len(repeated),
      "max_reuse_of_target_action_pair":max(repeated.values(),default=0),
      "average_action_length_gap_percent":round(
         sum(lengths)/len(lengths)*100,2),
      "maximum_action_length_gap_percent":round(max(lengths)*100,2),
      "engineering_blockers":engineering_blockers,
      "paid_pilot_blockers":paid_pilot_blockers,
      "confirmatory_blockers":confirmatory_blockers,
      "note":"Author-led semantic review is not independent external validation."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--enforce-ready",action="store_true",
                   help="Require readiness for implementing compatibility runner")
    p.add_argument("--enforce-paid-ready",action="store_true",
                   help="Require actual paid pilot authorization and hard spend control")
    args=p.parse_args()
    result=report()
    print(json.dumps(result,indent=2))
    if args.enforce_paid_ready and not result["ready_for_paid_pilot"]:
        return 2
    if args.enforce_ready and not result["ready_to_implement_compatibility_runner"]:
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
