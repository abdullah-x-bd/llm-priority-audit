# V3 offline primary-estimand precision planning

**Date:** 10 October 2026. **No actual v3 model decisions were observed.** This is synthetic planning only, *not* measured power for real models, nor a pre-registration.

## Scope and assumptions

The proposed primary outcome is the salient-minus-plain **Q choice-rate difference at Q quality minus N quality = -4**, over 600 matched pairs: 60 main contexts, five models, and two paired layouts. Four authored contexts share each of 15 mechanisms nested in three domains. We do not count 600 pairs as 600 independent mechanisms.

We simulated **1,500 replicated datasets for each of 18 settings**, varying the plain-frame mean Q-selection probability (0.20, 0.50, 0.80), imposed additive average salient-frame effect (0, 5, or 10 percentage points) and heterogeneity in mechanism-level framing effect (SD 3 or 8 percentage points). Mechanism, context and model baseline logit shifts had SD 0.7, 0.5 and 0.4. Matched frames share underlying baseline propensities but have separately drawn binary choices. Probabilities are truncated to [0.001, 0.999]. We estimated frame differences within mechanism and used equal domain weights and a stratified, 15-mechanism t-style interval (nominal df 12).

See [reproducible simulation code](../scripts/v3_precision_simulation.py) (NumPy required). These are **hypothetical data-generation models**, not empirical estimates of real model behavior.

## Selected planning results

| Baseline Q rate | True average frame effect | Between-mechanism effect SD | Detection at nominal 5% | Mean 95% CI half-width |
|---|---:|---:|---:|---:|
| 20% | 0 pp | 3 pp | 5.3% | 5.1 pp |
| 20% | 5 pp | 3 pp | 44.0% | 5.3 pp |
| 20% | 5 pp | 8 pp | 33.2% | 6.6 pp |
| 20% | 10 pp | 3 pp | 95.5% | 5.5 pp |
| 20% | 10 pp | 8 pp | 82.9% | 6.7 pp |
| 50% | 0 pp | 3 pp | 4.6% | 5.9 pp |
| 50% | 5 pp | 3 pp | 37.9% | 5.9 pp |
| 50% | 5 pp | 8 pp | 25.5% | 7.1 pp |
| 50% | 10 pp | 3 pp | 92.4% | 5.8 pp |
| 50% | 10 pp | 8 pp | 78.5% | 7.0 pp |
| 80% | 0 pp | 3 pp | 5.3% | 5.1 pp |
| 80% | 5 pp | 8 pp | 30.3% | 6.1 pp |
| 80% | 10 pp | 8 pp | 81.7% | 5.7 pp |

All simulated detection proportions have Monte Carlo error. This simple simulation does not represent token sampling dependence, temporal drift, provider switching, hard model-level ceilings, correlated domain shocks, measurement disagreement or reviewer-based stimulus exclusion. Real calibration may show very different variation.

## Decision implications

1. **Five percentage points is unlikely to be detected reliably** by the proposed 600-pair primary comparison under many plausible dependencies. Failure to reject a five-point effect will not prove absence.
2. **Ten percentage points is a more realistic planning scale** under these assumptions, with simulated detection ranging roughly 78.5% to 95.5% in the illustrated settings, not guaranteed in the actual task.
3. The 6,000-call total includes several descriptive secondary cost levels; it does **not** increase the number of independent main-family mechanisms beyond 15. Increasing only repeated prompts cannot solve a cluster-level variation problem.
4. The **six-family diagnostic is far too small** to establish true sampling precision for a full main. It can test basic outcome sensitivity to varying recorded quality. A substantive external review and additional robust simulation should evaluate whether the 15 mechanisms support main causal generalization.

Do **not** authorize paid main research solely because this simulated detector sometimes has high power. The external semantic review, provider preflight, calibration pass, estimand freeze and genuine preregistration remain blocking gates. Do not adjust the -4 primary comparison, effect-size target or exclusions after viewing calibration or main responses without explicitly declaring a new study.

**Offline planning status: completed. V3 scientific approval and paid collection status: NO-GO.**
