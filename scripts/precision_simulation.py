#!/usr/bin/env python3
"""Assumption-based planning simulation, NOT observed LLM results.

Approximates the matched frame contrast in a zero-quality-delta, operator-N arm
with correlated scenario-family difficulty, five selected models and two
layout samples. Normal-based intervals are only diagnostics, NOT the final
preregistered CI method.
"""
import argparse
import json
import math
import random
import statistics

DEFAULT_REPS = 600
SCENARIOS = 60
MODELS = 5
LAYOUTS = 2
SEED = 20261010

def experiment(rng, baseline, effect, family_sd, effect_sd):
    fam_effects = []
    for family in range(SCENARIOS):
        base = min(0.99, max(0.001, baseline + rng.gauss(0, family_sd)))
        true_effect = effect + rng.gauss(0, effect_sd)
        total = 0
        for model in range(MODELS):
            # Common model-specific response variation in matched frame calls.
            model_bias = rng.gauss(0, 0.015)
            neutral = min(0.99, max(0.001, base + model_bias))
            priority = min(0.99, max(0.001, neutral + true_effect))
            for _ in range(LAYOUTS):
                total += int(rng.random() < priority) - int(rng.random() < neutral)
        fam_effects.append(total / (MODELS * LAYOUTS))
    # Preserve three-domain, 20-family stratification.
    per_domain = [fam_effects[k*20:(k+1)*20] for k in range(3)]
    estimate = sum(statistics.mean(xs) for xs in per_domain) / 3
    se_sq = sum(statistics.variance(xs) / len(xs) for xs in per_domain) / 9
    se = math.sqrt(se_sq)
    # Degenerate all-zero data are NOT "certain". Such runs need conservative
    # uncertainty analysis outside this illustration.
    halfwidth = 1.96 * se if se > 0 else None
    detected = bool(se > 0 and abs(estimate) > 1.96 * se)
    return estimate, halfwidth, detected

def simulate(replications=DEFAULT_REPS):
    rng = random.Random(SEED)
    scenarios = []
    for base in (0.01, 0.05, 0.15):
        for effect in (0.0, 0.02, 0.05, 0.10):
            results = [experiment(rng, base, effect, family_sd=0.07,
                                  effect_sd=0.04)
                       for _ in range(replications)]
            hw = [x[1] for x in results if x[1] is not None]
            scenarios.append({
                "baseline_override_probability": base,
                "assumed_additive_frame_effect": effect,
                "simulations": replications,
                "mean_estimate": round(statistics.mean(x[0] for x in results), 4),
                "mean_normal_95ci_halfwidth": round(statistics.mean(hw), 4) if hw else None,
                "approx_detection_rate": round(sum(x[2] for x in results) / replications, 3),
                "degenerate_zero_variance_runs": sum(x[1] is None for x in results),
            })
    return {"status": "planning assumptions only, no model data",
            "seed": SEED, "families": SCENARIOS, "models": MODELS,
            "layouts_per_frame": LAYOUTS, "scenarios": scenarios}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replications", type=int, default=DEFAULT_REPS)
    args = p.parse_args()
    if args.replications < 20 or args.replications > 100000:
        p.error("replications must be between 20 and 100000")
    print(json.dumps(simulate(args.replications), indent=2))

if __name__ == "__main__":
    main()
