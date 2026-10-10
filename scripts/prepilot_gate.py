#!/usr/bin/env python3
"""Independent pre-pilot readiness audit. This tool makes NO model requests.

Exit 0 in reporting mode even when scientific review is incomplete.
Use --enforce-ready to fail closed (exit 2) on all documented blockers.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path
from expand_design import load_families, build_manifest
from validate_scenarios import audit

def report():
    main, pilot = load_families("main"), load_families("pilot")
    all_records = main + pilot
    summary = []
    blocking = []
    for phase in ("main","pilot"):
        a = audit(phase)
        summary.append({k:a[k] for k in ("phase","families","trial_templates_per_model","errors")})
        if a["errors"]:
            blocking.append(phase + " has structural validation failures")
    unsigned = [f["family_id"] for f in all_records if
                not f["quality_review"].get("instruction_unambiguous")]
    approved = [f["family_id"] for f in all_records if
                f["quality_review"].get("approved_for_pilot")]
    if unsigned: blocking.append(f"Independent semantic approval outstanding for {len(unsigned)} families")
    if len(approved) != len(all_records):
        blocking.append("Approval records not complete: study is not authorized for pilots by automated provenance")
    target_pairs = {(f["domain"],f["action_q"],f["action_n"]) for f in main}
    control_pairs = {(f["domain"],f["neutral_action_q"],f["neutral_action_n"]) for f in main}
    avg_target = sum(len(f["action_q"])+len(f["action_n"]) for f in main)/len(main)
    avg_control = sum(len(f["neutral_action_q"])+len(f["neutral_action_n"]) for f in main)/len(main)
    imbalance = abs(avg_target-avg_control)/avg_target
    if imbalance > 0.10:
        blocking.append("Control pair descriptions differ in mean length by >10%; semantic/lexical matching requires review")
    repeated_pairs = collections.Counter(
        (f["domain"],f["action_q"],f["action_n"]) for f in main)
    if max(repeated_pairs.values()) > 2:
        blocking.append("Main scenarios reuse each action-description pair across many contexts; independent semantic replication is limited")
    # Future gates cannot be inferred from code health.
    blocking.extend([
        "Independent neutral-control comparability and signoff not documented",
        "OpenRouter model/provider compatibility and billing preflight not completed",
        "Preregistered statistical inference and calibrated precision threshold not frozen"
    ])
    return {
        "study": "LLM Priority Audit", "stage": "pre-OpenRouter dry-run",
        "ready_for_paid_pilot": not blocking, "ready_for_confirmatory_run": False,
        "automatic_checks": summary,
        "expected_main_templates_per_model": len(build_manifest("main")),
        "expected_pilot_templates_per_model": len(build_manifest("pilot")),
        "unique_target_action_pairs_main": len(target_pairs),
        "unique_control_action_pairs_main": len(control_pairs),
        "max_target_pair_reuse": max(repeated_pairs.values()),
        "average_target_pair_characters_main": round(avg_target,2),
        "average_control_pair_characters_main": round(avg_control,2),
        "control_to_target_length_ratio": round(avg_control/avg_target,3),
        "unsigned_semantic_approvals": len(unsigned),
        "blocking_gates": blocking,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enforce-ready", action="store_true")
    args = parser.parse_args()
    r = report()
    print(json.dumps(r,indent=2))
    return 2 if (args.enforce_ready and not r["ready_for_paid_pilot"]) else 0

if __name__ == "__main__":
    raise SystemExit(main())
