#!/usr/bin/env python3
"""Post-collection classification from archived RAW API pilot envelopes.

This never sends OpenRouter requests and never overwrites the original archive.
Older successful pilot records may not have a raw envelope because the
capture-first protocol was introduced after 584 existing observations.
"""
import argparse
import collections
import json
from pathlib import Path
from expand_design import build_manifest
from raw_capture import classify_saved_event
from research_pipeline import ROSTER

def audit_checkpoint(source):
    state=json.loads(Path(source).read_text(encoding="utf-8"))
    manifest={x["trial_id"]:x for x in build_manifest("pilot")}
    result=[]
    counts=collections.Counter()
    events=state.get("raw_events",[])
    for event in events:
        if not isinstance(event,dict):
            raise ValueError("INVALID_RAW_EVENT")
        if event.get("expected_model") not in ROSTER:
            raise ValueError("UNKNOWN_EXPECTED_MODEL")
        trial=manifest.get(event.get("trial_id"))
        if trial is None:
            raise ValueError("UNKNOWN_RAW_TRIAL_ID")
        classified=classify_saved_event(event,trial)
        result.append(classified)
        counts[classified["category"]]+=1
    indices=[x["index"] for x in result]
    if len(indices)!=len(set(indices)):
        raise ValueError("DUPLICATE_RAW_EVENT_INDICES_REVIEW_REQUIRED")
    observed=len(state.get("collected",[]))
    return {
        "trial_attempt_rows":observed,
        "raw_events_available":len(events),
        "older_rows_without_raw_envelopes":max(0,observed-len(events)),
        "raw_capture_coverage_note":"Older responses have canonical records only. Do not claim full raw retention.",
        "category_counts":dict(sorted(counts.items())),
        "classifications":result,
        "method":"OFFLINE_ONLY_NO_ADDITIONAL_MODEL_INFERENCE",
        "research_status":"EXPLORATORY_PILOT_DO_NOT_USE_AS_CONFIRMATORY",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=audit_checkpoint(args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="classifications"},indent=2))
if __name__=="__main__":
    main()
