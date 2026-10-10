#!/usr/bin/env python3
"""Fail-closed gate for genuinely completed double-blind independent source reviews.

Blank templates and author-entered approval flags alone are NOT independent review.
Human identity and provenance still require out-of-band verification.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
from pathlib import Path
from expand_design import load_families
from generate_blind_review import REVIEW_CATEGORIES

def audit(path):
    expected={x["family_id"] for x in load_families("main")}
    with Path(path).open(encoding="utf-8",newline="") as stream:
        ratings=list(csv.DictReader(stream))
    group=collections.defaultdict(list)
    invalid_ids=[]
    for r in ratings:
        fid=r.get("family_id","")
        if fid not in expected: invalid_ids.append(fid)
        else: group[fid].append(r)
    flagged=[]
    for fid in sorted(expected):
        rows=group[fid]
        issues=[]
        if len(rows)!=2:
            issues.append("EXPECTED_TWO_REVIEWS")
        ids=[r.get("actual_reviewer_id","").strip() for r in rows]
        if len(ids)!=2 or any(not x for x in ids) or len(set(ids))!=2:
            issues.append("DISTINCT_VERIFIABLE_REVIEWER_IDS_REQUIRED")
        for r in rows:
            if not r.get("independent_affiliation","").strip():
                issues.append("INDEPENDENT_AFFILIATION_MISSING")
            if not r.get("reviewer_signature_or_confirmed_email","").strip():
                issues.append("SIGNED_REVIEW_PROVENANCE_MISSING")
            if not r.get("date_utc","").strip():
                issues.append("REVIEW_DATE_MISSING")
            if r.get("reviewed_blinded_X_Y","").strip().lower()!="yes":
                issues.append("BLINDING_ATTESTATION_MISSING")
            for name in REVIEW_CATEGORIES:
                if r.get("rating_"+name,"").strip().lower()!="pass":
                    issues.append("REVIEW_CRITERION_NOT_APPROVED_"+name)
            if r.get("overall_decision","").strip().lower()!="approve":
                issues.append("FAMILY_NOT_APPROVED")
        if issues:
            flagged.append({"family_id":fid,"issues":sorted(set(issues))})
    return {
        "main_families_required":len(expected),
        "expected_independent_reviews":len(expected)*2,
        "rows_received":len(ratings),
        "invalid_family_ids":invalid_ids,
        "families_with_unresolved_reviews":len(flagged),
        "first_unresolved":flagged[:20],
        "status":"REVIEW_RECORDS_PRESENT_NEED_EXTERNAL_PROVENANCE_CHECK"
            if not flagged and not invalid_ids and len(ratings)==120 else
            "NO_GO_INDEPENDENT_REVIEW_PENDING",
        "warning":"Passing this mechanical gate NEVER substitutes for verifying reviewer identities and actual independent signoff."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.input)
    print(json.dumps(report,indent=2))
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return 0 if report["status"]=="REVIEW_RECORDS_PRESENT_NEED_EXTERNAL_PROVENANCE_CHECK" else 2

if __name__=="__main__":
    raise SystemExit(main())
