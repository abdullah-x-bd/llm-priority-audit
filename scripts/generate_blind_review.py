#!/usr/bin/env python3
"""Create blinded, output-free human review packets for preconfirmatory v1 stimuli.

A and B here mean 'version 1/2' of a paired prompt, not experimental action
letters. Unblinding map is written separately. Never marks external approval.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from expand_design import build_manifest,load_families

REVIEW_CATEGORIES=(
 "mutually_exclusive_next_steps","same_task_control_comparability",
 "operator_instruction_unambiguous","numeric_payoff_coherence",
 "plausibility_of_no_hidden_consequences","equal_specificity_and_default_status",
 "neutral_control_lexical_valence","mechanism_substantive_distinctiveness",
 "third_party_safety_confounds","construct_difference_only",
)
SCORING=("pass","revise","reject")
SEED="blind-review-v1-2026-10-10"

def make_rows():
    prompts=[]
    unblinding=[]
    for phase in ("pilot","main"):
        manifests=build_manifest(phase)
        mapping={(t["family_id"],t["frame"],t["condition"],t["directive"],t["layout"]):t
                 for t in manifests}
        families=load_families(phase)
        for family in sorted(families,key=lambda r:r["family_id"]):
            fid=family["family_id"]
            pair={
                fr:mapping[fid,fr,"zero","N","layout0"]
                for fr in ("priority","neutral")
            }
            flip=int(hashlib.sha256((SEED+":"+fid).encode("utf-8")).hexdigest(),16)%2==1
            x,y=(("neutral","priority") if flip else ("priority","neutral"))
            row={
                "review_packet_id":"BLIND-"+fid,
                "phase":"practice_pilot" if phase=="pilot" else "external_main_review",
                "domain":family["domain"],
                "mechanism":family["mechanism"],
                "family_id":fid,
                "title":family["title"],
                "version_X_prompt":pair[x]["user_message"],
                "version_Y_prompt":pair[y]["user_message"],
                "version_X_sha256":pair[x]["request_sha256"],
                "version_Y_sha256":pair[y]["request_sha256"],
                "instructions":"Assess both versions independently for coherence, then compare their construct and neutrality; no model outcomes are shown.",
            }
            prompts.append(row)
            unblinding.append({
                "family_id":fid,"version_X_actual_frame":x,
                "version_Y_actual_frame":y,
                "version_X_request_sha256":pair[x]["request_sha256"],
                "version_Y_request_sha256":pair[y]["request_sha256"],
            })
    assert len(prompts)==66 and len(unblinding)==66
    return prompts,unblinding

def write_csv(path,rows,fieldnames):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def generate(out):
    prompts,map_rows=make_rows()
    write_csv(out/"blind-prompt-pairs.csv",prompts,list(prompts[0]))
    ratings=[]
    for p in prompts:
        if p["phase"]=="practice_pilot":
            continue
        for reviewer_number in (1,2):
            row={
                "packet_id":p["review_packet_id"],
                "family_id":p["family_id"],
                "reviewer_slot":str(reviewer_number),
                "actual_reviewer_id":"",
                "independent_affiliation":"",
                "date_utc":"",
                "reviewed_blinded_X_Y":"",  # must be set yes after actual review
            }
            row.update({f"rating_{x}":"" for x in REVIEW_CATEGORIES})
            row.update({
                "overall_decision":"",
                "documented_confound":"",
                "suggested_revision":"",
                "reviewer_signature_or_confirmed_email":"",
            })
            ratings.append(row)
    write_csv(out/"blank-reviewer-ratings.csv",ratings,list(ratings[0]))
    write_csv(out/"do-not-send-unblinding-key.csv",map_rows,list(map_rows[0]))
    readme=[
      "# Independent review packet", "",
      "The blank ratings are **not independent approvals**.",
      "Send blind-prompt-pairs.csv to reviewers. Hold do-not-send-unblinding-key.csv privately.",
      "Two separate reviewers must assess each of the 60 main families; do not fill",
      "reviewer identity, decisions, dates or signatures on their behalf.",
      "Each rating must be pass, revise or reject, with a concise rationale for a failing item.",
      "Reviewers must not see the pilot outputs, treatment labels or hypothesis direction.",
      "Two pilot source families per domain are included only as practice examples.",
      "Blind versions differ in descriptions but maintain prompt labels and known score parity.",
      "Version X/Y is independent of the A/B action choice inside prompts.",
      "",
      "## Blocking criteria",
      "",
      "Any reject on instruction clarity, payoff plausibility, paired-control comparability,",
      "or concealed safety implications blocks confirmatory readiness. Disagreements require",
      "recorded reconciliation and fresh review of any edited family.",
      "",
      "Do not claim a successful review until verified signoffs are archived.",
      "",
    ]
    (out/"README.md").write_text("\n".join(readme),encoding="utf-8")
    return {"pairs":len(prompts),"main_pairs":60,"practice_pairs":6,
            "blank_main_reviewer_slots":len(ratings),
            "external_reviewer_signoffs_completed":0,
            "key_file_not_for_reviewers":str(out/"do-not-send-unblinding-key.csv")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(generate(args.output_dir),indent=2))

if __name__=="__main__":
    main()
