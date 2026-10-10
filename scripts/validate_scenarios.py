#!/usr/bin/env python3
"""Offline audit of v1.0 scenarios, counterfactual text and factorial coverage."""
from __future__ import annotations
import collections
import hashlib
import json
import re
import sys
from expand_design import (
    DOMAINS, FRAMES, LEVELS, DIRECTIVES, LAYOUTS,
    ROOT, load_families, layout_assignment, build_manifest, display_mapping,
    SYSTEM_MESSAGE, COMMON_OUTCOME
)

PREFIX = {"continuation": "CONT", "reversibility": "REVR", "verification": "VERF"}
REQUIRED = {
    "family_id", "domain", "title", "context", "action_q", "action_n",
    "neutral_action_q", "neutral_action_n", "mechanism", "outcomes",
    "operator_authority", "quality_review"
}
PAYOFF_FIELDS = {"q_quality", "n_quality", "q_extra_cost", "n_extra_cost"}
EXPECTED_FAMILIES = {"main": 20, "pilot": 2}
EXTRA_COST = 0

def audit(phase, root=ROOT):
    errors = []
    families = load_families(phase, root=root)
    by_domain = collections.Counter(f.get("domain") for f in families)
    for d in DOMAINS:
        if by_domain[d] != EXPECTED_FAMILIES[phase]:
            errors.append(f"{d}: expected {EXPECTED_FAMILIES[phase]} families")
    for field in ("family_id", "title", "context"):
        vals = [str(f.get(field, "")).strip().casefold() for f in families]
        if len(set(vals)) != len(vals):
            errors.append(f"Duplicate {field}")
    mechanism_counts = collections.defaultdict(set)
    repeated_mechanisms = collections.Counter()
    for f in families:
        fid = f.get("family_id", "UNKNOWN")
        if set(f) != REQUIRED:
            errors.append(f"{fid}: wrong scenario fields")
        if f.get("domain") not in DOMAINS:
            errors.append(f"{fid}: unknown domain")
            continue
        mechanism_counts[f["domain"]].add(f.get("mechanism"))
        repeated_mechanisms[(f["domain"], f.get("mechanism"))] += 1
        if re.fullmatch(PREFIX[f["domain"]] + r"-\d{3}", fid) is None:
            errors.append(f"{fid}: wrong ID")
        if len(f.get("title", "")) < 10 or len(f.get("context", "")) < 50:
            errors.append(f"{fid}: short title/context")
        texts = [f.get(k, "") for k in
                 ("action_q", "action_n", "neutral_action_q", "neutral_action_n")]
        if len(set(texts)) != 4 or any(len(s) < 10 for s in texts):
            errors.append(f"{fid}: action descriptions missing or duplicated")
        if len(f.get("operator_authority", "")) < 20:
            errors.append(f"{fid}: inadequate authority text")
        review = f.get("quality_review", {})
        if review.get("mathematical_integrity") is not True:
            errors.append(f"{fid}: no recorded mathematical audit")
        if review.get("approved_for_pilot") is True and (
            review.get("instruction_unambiguous") is not True):
            errors.append(f"{fid}: approved without independent clarity review")
        payoffs = f.get("outcomes", {})
        if set(payoffs) != set(LEVELS):
            errors.append(f"{fid}: missing payoff level")
            continue
        baseline = payoffs["zero"].get("n_quality")
        for level, expected in (("positive", 10), ("zero", 0), ("negative", -10)):
            p = payoffs[level]
            if set(p) != PAYOFF_FIELDS:
                errors.append(f"{fid} {level}: wrong payoff fields")
                continue
            if p["q_quality"] - p["n_quality"] != expected:
                errors.append(f"{fid} {level}: wrong contrast")
            if p["n_quality"] != baseline:
                errors.append(f"{fid} {level}: alternative payoff drift")
            if not all(0 <= p[k] <= 100 for k in ("q_quality", "n_quality")):
                errors.append(f"{fid} {level}: out-of-range payoff")
            if p["q_extra_cost"] != EXTRA_COST or p["n_extra_cost"] != EXTRA_COST:
                errors.append(f"{fid} {level}: parity cost violated")
    for domain in DOMAINS:
        expected = 5 if phase == "main" else 2
        if len(mechanism_counts[domain]) != expected:
            errors.append(f"{domain}: expected {expected} distinct mechanisms, found {len(mechanism_counts[domain])}")
    expected_each_mechanism = 4 if phase == "main" else 1
    for (domain, mechanism), n in repeated_mechanisms.items():
        if n != expected_each_mechanism:
            errors.append(f"{domain}/{mechanism}: found {n} contexts; expected {expected_each_mechanism}")
    trials = build_manifest(phase, root=root)
    if len(trials) != len(families) * 24:
        errors.append("Incorrect number of factorial variants")
    if len({t["trial_id"] for t in trials}) != len(trials):
        errors.append("Duplicate trial IDs")
    assigned = layout_assignment(families)
    for domain in DOMAINS:
        values = collections.Counter(assigned[f["family_id"]] for f in families
                                     if f["domain"] == domain)
        if values[0] != values[1]:
            errors.append(f"{domain}: pairing types not balanced")
    by_family = collections.defaultdict(list)
    for t in trials:
        fid = t["family_id"]
        by_family[fid].append(t)
        q_label, n_label, order = display_mapping(t["pairing"], t["layout"])
        if (t["q_label"], t["n_label"], t["order"]) != (
            q_label, n_label, "Q_first" if order[0] == "Q" else "N_first"):
            errors.append(f"{t['trial_id']}: layout/label mismatch")
        if t["authorized_label"] != (
            t["q_label"] if t["directive"] == "Q" else t["n_label"]):
            errors.append(f"{t['trial_id']}: bad authorized action mapping")
        if t["system_message"] != SYSTEM_MESSAGE or COMMON_OUTCOME not in t["user_message"]:
            errors.append(f"{t['trial_id']}: common prompt changed")
        payload = json.dumps(
            [{"role": "system", "content": t["system_message"]},
             {"role": "user", "content": t["user_message"]}],
            ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        if hashlib.sha256(payload.encode()).hexdigest() != t["request_sha256"]:
            errors.append(f"{t['trial_id']}: wrong request hash")
        if (t["user_message"].count("A. ") != 1 or
            t["user_message"].count("B. ") != 1):
            errors.append(f"{t['trial_id']}: missing A/B action")
    expected_cells = {(frame, v, d, l) for frame in FRAMES for v in LEVELS
                      for d in DIRECTIVES for l in LAYOUTS}
    for family in families:
        fid = family["family_id"]
        records = by_family[fid]
        cells = {(r["frame"], r["condition"], r["directive"], r["layout"])
                 for r in records}
        if cells != expected_cells or len(records) != len(expected_cells):
            errors.append(f"{fid}: missing/duplicate factorial cells")
        for record in records:
            content = record["user_message"]
            expected_q = (family["action_q"] if record["frame"] == "priority"
                          else family["neutral_action_q"])
            expected_n = (family["action_n"] if record["frame"] == "priority"
                          else family["neutral_action_n"])
            if content.count(family["context"]) != 1:
                errors.append(f"{record['trial_id']}: context mismatch")
            if content.count(expected_q) != 1 or content.count(expected_n) != 1:
                errors.append(f"{record['trial_id']}: frame texts wrong")
            wrong = ("neutral_action_q", "neutral_action_n") if record["frame"] == "priority" else ("action_q", "action_n")
            if any(family[k] in content for k in wrong):
                errors.append(f"{record['trial_id']}: semantic frame leakage")
            p = family["outcomes"][record["condition"]]
            for act, label in (("q", record["q_label"]), ("n", record["n_label"])):
                if content.count(
                    f"{label} | {p[act + '_quality']} | {p[act + '_extra_cost']}"
                ) != 1:
                    errors.append(f"{record['trial_id']}: payoff mapping error")
        # In any fixed (level,directive,layout), frame changes descriptions only.
        for level in LEVELS:
            for directive in DIRECTIVES:
                for layout in LAYOUTS:
                    a = next(r for r in records if (r["frame"], r["condition"], r["directive"], r["layout"]) ==
                             ("priority", level, directive, layout))
                    b = next(r for r in records if (r["frame"], r["condition"], r["directive"], r["layout"]) ==
                             ("neutral", level, directive, layout))
                    for key in ("q_label", "n_label", "authorized_label", "order", "system_message"):
                        if a[key] != b[key]:
                            errors.append(f"{fid}/{level}/{directive}/{layout}: frame contamination ({key})")
    return {
        "phase": phase,
        "families": len(families),
        "trial_templates_per_model": len(trials),
        "mechanisms_per_domain": {d: len(mechanism_counts[d]) for d in DOMAINS},
        "automated_integrity_pass": not errors,
        "errors": errors,
        "semantic_review_pending": sum(not f["quality_review"].get("instruction_unambiguous") for f in families),
    }

def main():
    reports = [audit("main"), audit("pilot")]
    print(json.dumps({"audit": reports, "all_automated_checks_pass":
                      all(r["automated_integrity_pass"] for r in reports)}, indent=2))
    return 0 if all(r["automated_integrity_pass"] for r in reports) else 1

if __name__ == "__main__":
    sys.exit(main())
