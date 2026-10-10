#!/usr/bin/env python3
"""Offline scenario, factorial, and counterfactual integrity audit.

Uses only the Python standard library. It is deliberately independent of OpenRouter.
"""
from __future__ import annotations
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

from expand_design import (ROOT, DOMAINS, LEVELS, DIRECTIVES, ORDERS,
                           load_families, build_manifest, label_assignment)

REQUIRED = {
    "family_id", "domain", "title", "context", "action_q", "action_n",
    "outcomes", "operator_authority", "quality_review"
}
EXPECTED_PREFIX = {"continuation": "CONT", "reversibility": "REVR",
                   "verification": "VERF"}
COST_FIELDS = ("q_extra_cost", "n_extra_cost")
FAMILY_COUNT = {"main": 20, "pilot": 2}

def audit(phase):
    errors, warnings = [], []
    families = load_families(phase)
    grouped = collections.Counter(r.get("domain") for r in families)
    for domain in DOMAINS:
        if grouped[domain] != FAMILY_COUNT[phase]:
            errors.append(f"{phase}: {domain} has {grouped[domain]} families")
    ids = [r.get("family_id") for r in families]
    if len(ids) != len(set(ids)):
        errors.append("Repeated family ID")
    for attr in ("title", "context", "action_q", "action_n"):
        values = [r.get(attr, "").casefold().strip() for r in families]
        if len(values) != len(set(values)):
            errors.append("Repeated " + attr)

    for row in families:
        fid = row.get("family_id", "UNKNOWN")
        if set(row) != REQUIRED:
            errors.append(f"{fid}: fields do not match the scenario schema")
        domain = row.get("domain")
        if domain not in EXPECTED_PREFIX:
            errors.append(f"{fid}: unknown domain")
            continue
        if re.fullmatch(EXPECTED_PREFIX[domain] + r"-\d{3}", fid) is None:
            errors.append(f"{fid}: bad ID pattern")
        if len(row.get("context", "")) < 50 or len(row.get("title", "")) < 10:
            errors.append(f"{fid}: short context/title")
        if min(len(row.get("action_q", "")), len(row.get("action_n", ""))) < 10:
            errors.append(f"{fid}: short action")
        if row.get("action_q") == row.get("action_n"):
            errors.append(f"{fid}: actions identical")
        if len(row.get("operator_authority", "")) < 20:
            errors.append(f"{fid}: missing operator authority")
        qr = row.get("quality_review", {})
        if qr.get("approved_for_pilot") is not False:
            warnings.append(f"{fid}: review flag should remain false until approved")
        if not all(qr.get(k) is True for k in
                   ("mathematical_integrity", "instruction_unambiguous")):
            errors.append(f"{fid}: source sanity review not passed")
        outcomes = row.get("outcomes", {})
        if set(outcomes) != set(LEVELS):
            errors.append(f"{fid}: incomplete outcomes")
            continue
        zero = outcomes["zero"]
        for condition, expected_delta in (("positive", 10), ("zero", 0), ("negative", -10)):
            p = outcomes[condition]
            if set(p) != {"q_quality", "n_quality", "q_extra_cost", "n_extra_cost"}:
                errors.append(f"{fid}/{condition}: bad payoff fields")
                continue
            if p["q_quality"] - p["n_quality"] != expected_delta:
                errors.append(f"{fid}/{condition}: wrong causal payoff difference")
            if not (0 <= p["q_quality"] <= 100 and 0 <= p["n_quality"] <= 100):
                errors.append(f"{fid}/{condition}: quality outside 0..100")
            if p["n_quality"] != zero["n_quality"]:
                errors.append(f"{fid}/{condition}: alternative payoff not invariant")
            if any(p[k] != zero[k] for k in COST_FIELDS):
                errors.append(f"{fid}/{condition}: cost manipulation leak")
            if p["q_extra_cost"] != 2 or p["n_extra_cost"] != 0:
                errors.append(f"{fid}/{condition}: incorrect fixed resource cost")

    manifest = build_manifest(phase)
    if len(manifest) != len(families) * 12:
        errors.append(f"{phase}: wrong factorial expansion count")
    ids = [x["trial_id"] for x in manifest]
    if len(ids) != len(set(ids)):
        errors.append("Repeated trial_id")
    by_family = collections.defaultdict(list)
    for trial in manifest:
        by_family[trial["family_id"]].append(trial)
        if trial["authorized_label"] != (
            trial["q_label"] if trial["directive"] == "Q" else trial["n_label"]
        ):
            errors.append(f"{trial['trial_id']}: bad instruction label")
        if trial["q_label"] == trial["n_label"]:
            errors.append(f"{trial['trial_id']}: identical displayed option labels")
        if re.search(r"(?m)^A\. ", trial["user_message"]) is None:
            errors.append(f"{trial['trial_id']}: missing displayed A")
        if re.search(r"(?m)^B\. ", trial["user_message"]) is None:
            errors.append(f"{trial['trial_id']}: missing displayed B")
        combined = trial["system_message"] + "\n\n" + trial["user_message"]
        if hashlib.sha256(combined.encode()).hexdigest() != trial["request_sha256"]:
            errors.append(f"{trial['trial_id']}: incorrect request digest")
    for fid, trials in by_family.items():
        cells = {(x["condition"], x["directive"], x["order"]) for x in trials}
        expected = {(v, d, o) for v in LEVELS for d in DIRECTIVES for o in ORDERS}
        if cells != expected:
            errors.append(f"{fid}: missing or duplicate treatment cells")
        for condition in LEVELS:
            for directive in DIRECTIVES:
                two = [x for x in trials if x["condition"] == condition
                       and x["directive"] == directive]
                if len(two) != 2 or {x["order"] for x in two} != set(ORDERS):
                    errors.append(f"{fid}: display order imbalance")
        if len({x["q_label"] for x in trials}) != 1:
            errors.append(f"{fid}: label not constant within scenario family")
        if len({x["system_message"] for x in trials}) != 1:
            errors.append(f"{fid}: changing system message across arms")
        if len({x["request_sha256"] for x in trials}) != 12:
            errors.append(f"{fid}: repeated rendered prompt across distinct cells")

    labels = label_assignment(families)
    for domain in DOMAINS:
        counts = collections.Counter(labels[r["family_id"]] for r in families
                                     if r["domain"] == domain)
        if counts["A"] != counts["B"]:
            errors.append(f"{phase} {domain}: candidate label imbalance")

    # Check that the text outside the stimulus's designated factorial slots is invariant.
    # We reconstruct it from each structured source, and assert literal inclusion across arms.
    for family in families:
        trials = by_family[family["family_id"]]
        for t in trials:
            text = t["user_message"]
            for unchanged in (family["context"], family["action_q"], family["action_n"],
                              family["operator_authority"]):
                if text.count(unchanged) != 1:
                    errors.append(f"{t['trial_id']}: invariant text changed")
            for action in ("q", "n"):
                label = t["q_label"] if action == "q" else t["n_label"]
                payoff = family["outcomes"][t["condition"]]
                row = (f"{label} | {payoff[action + '_quality']} | "
                       f"{payoff[action + '_extra_cost']}")
                if text.count(row) != 1:
                    errors.append(f"{t['trial_id']}: wrong payoff or display label")
    return {
        "phase": phase, "family_count": len(families),
        "expanded_trial_templates": len(manifest),
        "by_domain": dict(grouped),
        "validation_errors": errors, "review_warnings": warnings,
        "review_status": "independent_human_review_pending",
    }

def main():
    reports = [audit("main"), audit("pilot")]
    problems = sum(len(r["validation_errors"]) for r in reports)
    print(json.dumps({"audit": reports, "all_automated_checks_pass": problems == 0},
                     indent=2))
    return 0 if not problems else 1

if __name__ == "__main__":
    sys.exit(main())
