#!/usr/bin/env python3
"""OFFLINE assumption-dependent V3 precision simulation.

Requires numpy. No API imports, model requests, network, or user credentials.
Uses 15 mechanism clusters nested in three domains, four contexts each,
five modeled response sources, two layouts, and paired frame choices.
Do not use synthetic power as evidence of actual model response rates.
"""
from __future__ import annotations
import json
import numpy as np

REPS = 1500
SEED = 20261010
T12_975 = 2.178812829  # two-sided 95% t critical value at df=12


def run_one(rng, baseline, treatment_shift, sd_effect, n=REPS):
    # shape (replication, domain, mechanism, context, model, layout)
    mechanism = rng.normal(0, .7, (n, 3, 5, 1, 1, 1))
    context = rng.normal(0, .5, (n, 3, 5, 4, 1, 1))
    model = rng.normal(0, .4, (n, 1, 1, 1, 5, 1))
    logit = np.log(baseline / (1.0 - baseline)) + mechanism + context + model
    p_plain = 1.0 / (1.0 + np.exp(-logit))
    mechanism_effect = rng.normal(0, sd_effect, (n, 3, 5, 1, 1, 1))
    p_salient = np.clip(p_plain + treatment_shift + mechanism_effect, .001, .999)
    shape = (n, 3, 5, 4, 5, 2)
    a = (rng.random(shape) < p_salient).astype(np.int8)
    b = (rng.random(shape) < p_plain).astype(np.int8)
    means = (a - b).mean(axis=(3, 4, 5))
    effect = means.mean(axis=(1, 2))
    # Stratified across domains: 5 independent mechanism means per domain;
    # 15 clusters total. Note exchangeability assumptions, not guaranteed.
    mechanism_variance = means.var(axis=2, ddof=1)
    se = np.sqrt(mechanism_variance.sum(axis=1) / (9 * 5))
    halfwidth = T12_975 * se
    return {
        "baseline_probability": baseline,
        "true_average_treatment_effect": treatment_shift,
        "mechanism_effect_sd": sd_effect,
        "replications": n,
        "simulated_two_sided_rejection_probability": round(
            float((np.abs(effect) > halfwidth).mean()), 3
        ),
        "mean_95pct_interval_halfwidth_probability_points": round(
            float(halfwidth.mean()), 3
        ),
        "mean_estimate": round(float(effect.mean()), 3),
    }


def main():
    rng = np.random.default_rng(SEED)
    results = [
        run_one(rng, baseline, effect, sd_effect)
        for baseline in (.2, .5, .8)
        for effect in (0.0, .05, .10)
        for sd_effect in (.03, .08)
    ]
    print(json.dumps({
        "planning_only": True,
        "v3_observed_data_included": False,
        "rng_seed": SEED,
        "assumed_mechanism_logit_sd": .7,
        "assumed_context_logit_sd": .5,
        "assumed_model_logit_sd": .4,
        "clusters": 15,
        "pairs": 600,
        "synthetic_results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
