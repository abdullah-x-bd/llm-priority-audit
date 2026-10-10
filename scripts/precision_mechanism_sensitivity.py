#!/usr/bin/env python3
"""Mechanism-clustering sensitivity, with only simulated Bernoulli choices.

The source design has 3 domains x 5 action mechanisms x 4 contexts.
These 15 repeated mechanism pairs can induce substantial dependence.
We contrast a naive family-level variance proxy against an alternative
mechanism-cluster variance proxy. Normal CIs are *illustrative*, not approved.
"""
from __future__ import annotations
import json
import math
import random
import statistics

SEED=20261010
REPS=500
DOMAINS=3
MECHANISMS=5
CONTEXTS=4
MODELS=5
LAYOUTS=2

def clamp(x):
    return max(0.001,min(0.999,x))

def simulate(base=.05, effect=.05, mech_sd=.06, scenario_sd=.015, reps=REPS):
    rng=random.Random(SEED+round(base*1000)+round(effect*1000))
    results=[]
    for _ in range(reps):
        family_diffs=[]
        per_domain_means=[]
        mechanism_diffs=[]
        for domain in range(DOMAINS):
            domain_diffs=[]
            mechanism_means=[]
            for mechanism in range(MECHANISMS):
                common_base=rng.gauss(0,mech_sd)
                common_effect=rng.gauss(0,mech_sd/2)
                diffs=[]
                for ctx in range(CONTEXTS):
                    local=rng.gauss(0,scenario_sd)
                    p0=clamp(base+common_base+local)
                    p1=clamp(p0+effect+common_effect)
                    total=0
                    for model in range(MODELS):
                        for layout in range(LAYOUTS):
                            total+=int(rng.random()<p1)-int(rng.random()<p0)
                    diff=total/(MODELS*LAYOUTS)
                    diffs.append(diff)
                    domain_diffs.append(diff)
                mechanism_means.append(statistics.mean(diffs))
            family_diffs.append(domain_diffs)
            mechanism_diffs.append(mechanism_means)
            per_domain_means.append(statistics.mean(domain_diffs))
        theta=statistics.mean(per_domain_means)
        # Both estimates are analytic normal-planning proxies only.
        family_se=math.sqrt(sum(statistics.variance(x)/len(x) for x in family_diffs)/9)
        mech_se=math.sqrt(sum(statistics.variance(x)/len(x) for x in mechanism_diffs)/9)
        results.append((theta,family_se,mech_se))
    return {
        "assumed_baseline_probability":base,
        "assumed_frame_effect":effect,
        "shared_mechanism_sd":mech_sd,
        "replications":reps,
        "mean_effect_estimate":round(statistics.mean(r[0] for r in results),4),
        "mean_95pct_halfwidth_family_naive":round(statistics.mean(1.96*r[1] for r in results),4),
        "mean_95pct_halfwidth_mechanism_cluster":round(statistics.mean(1.96*r[2] for r in results),4),
        "approx_family_naive_rejection_fraction":round(sum(abs(r[0])>1.96*r[1] for r in results if r[1]>0)/reps,3),
        "approx_mechanism_cluster_rejection_fraction":round(sum(abs(r[0])>1.96*r[2] for r in results if r[2]>0)/reps,3),
    }

if __name__=="__main__":
    summary=[simulate(base,effect,reps=100) for base,effect in
             ((0.01,0),(0.05,0),(0.05,0.02),(0.05,0.05),(0.15,0.05))]
    print(json.dumps({"status":"simulation, not actual model evidence",
                      "warning":"only 5 distinct action mechanisms per domain; neither normal CI is automatically valid",
                      "results":summary},indent=2))
