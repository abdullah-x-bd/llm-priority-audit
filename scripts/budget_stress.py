#!/usr/bin/env python3
"""Offline budget stress test, independent of OpenRouter credentials.

This estimates usage-dependent charges, not actual token usage or a safe
per-request maximum. An API execution spending cap must be enforced separately.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C = json.loads((ROOT/"config"/"pricing-assumptions.json").read_text(encoding="utf-8"))

def projected(input_tokens, output_tokens, include_pilot=True):
    total = 0.0
    details = []
    for m in C["models"]:
        count=C["main_requests_per_model"]+(C["pilot_requests_per_model"] if include_pilot else 0)
        cost=count * (m["input"]*input_tokens + m["output"]*output_tokens) / 1_000_000
        details.append({"model":m["id"],"calls":count,"estimated_usd":round(cost,4)})
        total+=cost
    return {"assumed_input_tokens_per_call":input_tokens,
            "assumed_total_billed_output_tokens_per_call":output_tokens,
            "includes_pilot":include_pilot,
            "estimated_usd":round(total,4),
            "exceeds_8_dollar_inference_budget":total > C["maximum_inference_budget_usd"],
            "model_costs":details}

def main():
    tests=[projected(i,o) for i,o in [(300,40),(500,100),(750,200),(1000,350)]]
    if not tests[-1]["exceeds_8_dollar_inference_budget"]:
        raise AssertionError("High-usage stress test should exceed the cap")
    print(json.dumps({"status":"planning estimates only, not a live budget preflight",
                      "model_count":len(C["models"]),
                      "runs":tests},indent=2))

if __name__ == "__main__":
    main()
