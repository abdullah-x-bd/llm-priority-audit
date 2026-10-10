#!/usr/bin/env python3
"""Six never behavior-tested v2 sensitivity families, matched to main mechanics.

Derived from previously authored CAL sources, NOT any of 60 v2 main responses.
This generator does not call model APIs. Source descriptions remain provisional
and require reviewer assessment before any paid calibration is authorized.
"""
from __future__ import annotations
import argparse,hashlib,json,random
from pathlib import Path
from expand_design import ROOT,render_trial,DOMAINS,FRAMES,DIRECTIVES,LAYOUTS,ORDER_SEED
from main_v2_matched_design import PATTERNS,COMMON_NOTES

CAL_SOURCE=ROOT/"data"/"calibration-v2"/"draft-families.jsonl"
PAIR={
    "batch_owner_handoff":"process_handoff",
    "stateful_parser_handoff":"state_retention",
    "retained_rollback":"rollback_checkpoint",
    "reopenable_archive":"editable_state",
    "repeat_consistency_check":"repeat_check",
    "independent_second_checker":"independent_crosscheck",
}
def cal_families():
    old=[json.loads(x) for x in CAL_SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(old)==6
    result=[]
    for f in old:
        mechanic=PAIR[f["mechanism"]]
        p=PATTERNS[mechanic]
        revised={**f,"context":f["context"].strip()+" "+COMMON_NOTES[f["domain"]],
             "mechanism":mechanic,"action_q":p["Q"],"action_n":p["N"],
             "neutral_action_q":p["q"],"neutral_action_n":p["n"],
             "operator_authority":"",
             "v2_review_status":"UNREVIEWED_HELDOUT_SENSITIVITY_CANDIDATE",
             "source_sha256":hashlib.sha256(json.dumps(f,sort_keys=True).encode()).hexdigest()}
        assert f["quality_review"]["approved_for_pilot"] is False
        result.append(revised)
    assert len(set(x["family_id"] for x in result))==6
    assert {d:sum(x["domain"]==d for x in result) for d in DOMAINS}=={d:2 for d in DOMAINS}
    return result
def manifest():
    result=[]
    for idx,f in enumerate(cal_families()):
        for frame in FRAMES:
            for directive in DIRECTIVES:
                for layout in LAYOUTS:
                    t=render_trial(f,frame,"zero",directive,layout,idx%2)
                    t["user_message"]=t["user_message"].replace(
                        "\nThe directive is deliberate regardless of the listed scores.","")
                    t["user_message"]=t["user_message"].replace("\n\nOperator directive:","\nOperator directive:")
                    msgs=[{"role":"system","content":t["system_message"]},
                          {"role":"user","content":t["user_message"]}]
                    serial=json.dumps(msgs,ensure_ascii=False,separators=(",",":"),sort_keys=True)
                    t["request_sha256"]=hashlib.sha256(serial.encode()).hexdigest()
                    t["trial_id"]="-".join((f["family_id"],frame,"zero",directive,layout))
                    t["phase"]="calibration_v2_draft"
                    t["v2_review_status"]="NOT_INDEPENDENTLY_APPROVED"
                    result.append(t)
    assert len(result)==48
    random.Random(ORDER_SEED+3).shuffle(result)
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result=manifest()
    a.output.write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result),encoding="utf-8")
    print(json.dumps({"calibration_families":6,"trial_prompts_per_model":48,
                      "all_five_models_planned":240,"model_requests":0,
                      "review":"PENDING","confirmatory":"BLOCKED"}))
if __name__=="__main__":main()
