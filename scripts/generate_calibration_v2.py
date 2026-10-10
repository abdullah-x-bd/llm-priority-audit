#!/usr/bin/env python3
"""Generate prospective, previously untested calibration prompt candidates.

No inference calls. No modifications to main or completed pilot source data.
All candidates remain blocked pending truly independent semantic review.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from expand_design import ROOT,render_trial
from propose_instruction_variants import revised_trial

SOURCE=ROOT/"data"/"calibration-v2"/"draft-families.jsonl"
STYLES=("strict_baseline","concise_operator","undirected_diagnostic")

def source_families():
    cases=[json.loads(x) for x in SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(cases)==6 and len({c["family_id"] for c in cases})==6
    by={}
    for r in cases:
        assert r["quality_review"]["approved_for_pilot"] is False
        assert r["quality_review"]["instruction_unambiguous"] is False
        assert r["family_id"].startswith("CAL-")
        by.setdefault(r["domain"],[]).append(r)
    assert {d:len(v) for d,v in by.items()}=={
        "continuation":2,"reversibility":2,"verification":2}
    return cases

def build():
    records=[]
    review=[]
    for domain in ("continuation","reversibility","verification"):
        family=[f for f in source_families() if f["domain"]==domain]
        for pairing,f in enumerate(family):
            for frame in ("priority","neutral"):
                for layout in ("layout0","layout1"):
                    src=render_trial(f,frame,"zero","N",layout,pairing)
                    src["trial_id"]="-".join((f["family_id"],frame,"zero","N",layout))
                    for style in STYLES:
                        records.append(revised_trial(src,f,style))
            # Two genuinely independent assessments per family, with source
            # priority/control versions concealed behind X/Y. No model outputs.
            flip=int(hashlib.sha256(("calibration-blinding:"+f["family_id"]).encode()).hexdigest(),16)%2
            action_X=(f["action_q"],f["action_n"]) if not flip else (
                f["neutral_action_q"],f["neutral_action_n"])
            action_Y=(f["neutral_action_q"],f["neutral_action_n"]) if not flip else (
                f["action_q"],f["action_n"])
            for reviewer_slot in (1,2):
                review.append({
                    "family_id":f["family_id"],"domain":domain,"title":f["title"],
                    "context":f["context"],"reviewer_slot":str(reviewer_slot),
                    "version_X_action_Q":action_X[0],"version_X_action_N":action_X[1],
                    "version_Y_action_Q":action_Y[0],"version_Y_action_N":action_Y[1],
                    "draft_authority_variants":"Strict final-authority plus repeated directive; concise single explicit operator directive; undirected preference with no directive.",
                    "action_comparability_pass_revise_reject":"",
                    "hidden_cost_plausibility_pass_revise_reject":"",
                    "single_operator_clarity_pass_revise_reject":"",
                    "no_directive_is_preference_only_yes_no":"",
                    "lexical_valence_pass_revise_reject":"",
                    "independent_reviewer_identity":"",
                    "independent_reviewer_affiliation":"",
                    "review_date_utc":"",
                    "external_signoff":"",
                    "feedback":"",
                })
    assert len(records)==6*2*2*3
    assert len({(r["trial_id"],r["style"]) for r in records})==len(records)
    return records,review

def generate(out):
    records,review=build()
    out.mkdir(parents=True,exist_ok=True)
    (out/"calibration-v2-unapproved.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in records),
        encoding="utf-8")
    with (out/"calibration-v2-blank-review.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(review[0]));writer.writeheader();writer.writerows(review)
    (out/"README.md").write_text(
        "# New calibration-v2 drafts\n\n"
        "72 unapproved prompts from six NEW never-tested contexts, kept separate from "
        "both the 60 main families and the prior six pilot families.\n\n"
        "The strict arm retains the original redundant operator reminder. "
        "The concise arm retains exactly one explicit operator directive. "
        "The undirected arm contains no operator directive and cannot measure overrides.\n\n"
        "All numeric scores are equal in this draft's parity condition. "
        "Twelve reviewer rows (two per family) are BLANK. Versions X/Y conceal the frame identities. No independent review has occurred. "
        "Do not submit these prompts to paid models or label them preregistered "
        "until the construct review, sample design and budget are approved.\n",
        encoding="utf-8")
    return {"new_source_families":6,"unapproved_prompt_variants":len(records),
            "blank_independent_review_slots":len(review),
            "reviewer_signoffs_completed":0,"paid_calls":0,
            "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest()}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(generate(a.output_dir),indent=2))

if __name__=="__main__":
    main()
