#!/usr/bin/env python3
"""Mechanism-aware type-I error, interval-width and detection calibration.

SIMULATED data only. No real model requests, tokens or responses.
Designed for 3 domains x 5 mechanisms/domain x 4 contexts/mechanism,
5 fixed model endpoints and 2 layouts. A mechanism, not each reused
context, is treated as the independent simulation unit.

This does not establish external generalization to all AI models or tasks.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import statistics

DOMAINS=3
MECHANISMS_PER_DOMAIN=5
CONTEXTS_PER_MECHANISM=4
MODELS=5
LAYOUTS=2
T_CRITICAL_DF12=2.17881283
SEED=20261010

def logistic(x):
    if x >= 0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)

def replicate(rng, base, effect, mechanism_sd, family_sd, effect_sd):
    """Paired simulated responses and stratified 15-cluster t approximation.

    Under the null effect=0 we set p(priority)=p(neutral) for each
    exact unit, avoiding the false treatment shift in earlier planning
    simulations. Nonzero effects may vary across mechanism clusters.
    """
    logit=math.log(base/(1-base))
    model_bias=[rng.gauss(0,0.25) for _ in range(MODELS)]
    strata=[]
    for domain in range(DOMAINS):
        means=[]
        for mechanism in range(MECHANISMS_PER_DOMAIN):
            common=rng.gauss(0,mechanism_sd)
            shift=0.0 if effect==0 else rng.gauss(0,effect_sd)
            subtotal=0
            for context in range(CONTEXTS_PER_MECHANISM):
                context_shift=rng.gauss(0,family_sd)
                for model in range(MODELS):
                    p0=logistic(logit+common+context_shift+model_bias[model])
                    p1=max(0.0001,min(0.9999,p0+effect+shift))
                    for layout in range(LAYOUTS):
                        subtotal+=int(rng.random()<p1)-int(rng.random()<p0)
            means.append(subtotal/(CONTEXTS_PER_MECHANISM*MODELS*LAYOUTS))
        strata.append(means)
    estimate=sum(statistics.mean(g) for g in strata)/DOMAINS
    # Exact variance form for 3 equally weighted strata of 5 clusters.
    se=math.sqrt(sum(statistics.variance(g)/len(g) for g in strata)/(DOMAINS**2))
    # No false certainty from all-zero data.
    flagged=bool(se>0 and abs(estimate)>T_CRITICAL_DF12*se)
    return estimate,T_CRITICAL_DF12*se,flagged

def calibrate(reps=1000, seed=SEED):
    regimes=[
      {"name":"moderate_cluster_variation","mechanism_sd":0.8,"family_sd":0.3,"effect_sd":0.025},
      {"name":"high_cluster_variation","mechanism_sd":1.4,"family_sd":0.3,"effect_sd":0.060},
    ]
    results=[]
    for regime_index,reg in enumerate(regimes):
        for base in (0.01,0.05,0.15):
            for effect in (0.0,0.02,0.05,0.10):
                rng=random.Random(seed+regime_index*1_000_000+int(base*1000)*1000+int(effect*1000))
                observed=[replicate(rng,base,effect,reg["mechanism_sd"],
                                    reg["family_sd"],reg["effect_sd"])
                          for _ in range(reps)]
                rejection=sum(z[2] for z in observed)/reps
                halfwidth=statistics.mean(z[1] for z in observed)
                results.append({
                    "regime":reg["name"],
                    "baseline_probability":base,
                    "assigned_additive_probability_effect":effect,
                    "replications":reps,
                    "mean_estimated_difference":round(statistics.mean(z[0] for z in observed),5),
                    "mean_halfwidth_nominal_95pct":round(halfwidth,5),
                    "approx_rejection_rate":round(rejection,4),
                    "mc_standard_error_rejection":round(math.sqrt(rejection*(1-rejection)/reps),4),
                    "interpretation":"null_rejection_calibration" if effect==0 else "assumption_conditional_detection"
                })
    return {
        "data_source":"synthetic simulation only",
        "models":MODELS,
        "domains":DOMAINS,
        "distinct_action_mechanism_clusters":DOMAINS*MECHANISMS_PER_DOMAIN,
        "contexts_per_cluster":CONTEXTS_PER_MECHANISM,
        "layouts":LAYOUTS,
        "inference_proxy":"stratified mechanism-cluster t-statistic, df12 critical",
        "t_critical":T_CRITICAL_DF12,
        "warning":"results depend on assumed response distributions, model routes and repeated-mechanism correlation; no empirical power guarantee",
        "results":results,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reps",type=int,default=1000)
    p.add_argument("--output",type=str,default="")
    args=p.parse_args()
    if not 100<=args.reps<=10000:
        p.error("--reps must be between 100 and 10000")
    result=calibrate(reps=args.reps)
    serialized=json.dumps(result,indent=2)+"\n"
    if args.output:
        from pathlib import Path
        fp=Path(args.output)
        fp.parent.mkdir(exist_ok=True,parents=True)
        fp.write_text(serialized,encoding="utf-8")
    print(serialized,end="")

if __name__=="__main__":
    main()
