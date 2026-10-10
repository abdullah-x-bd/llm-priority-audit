# Mechanism-aware statistical precision calibration

**Recorded 10 October 2026.** All results below use **synthetic Bernoulli choices**, not model responses. The reproducible GitHub Actions run is https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38040384401 .

## Design accounted for in calibration

We simulated the full structure of 3 domains, 5 underlying action mechanisms per domain, 4 source contexts per mechanism, 5 selected model endpoints, and 2 presentation layouts. We treat the **15 mechanisms** as the correlated units for statistical inference, rather than treating 60 contexts or 7,200 API calls as independent.

For the parity condition under operator instruction N, our candidate primary estimator is the equal-domain mean of the paired priority-minus-neutral valid-Q incidence contrast. Our candidate inferential approximation uses the variance of the five mechanism means within each domain and a two-sided Student-t critical value **2.17881283 for 12 degrees of freedom**. This is assumption-conditional, not a distribution-free or universally design-based interval.

We simulated two between-mechanism heterogeneity regimes, three neutral-frame baseline override rates (1%, 5%, 15%) and four assigned frame effects (0, 2, 5, 10 percentage points), with **1,000 independent replications** of each of 24 combinations. The corrected simulation preserves exactly equal underlying probabilities under a sharp null. For nonzero effects, bounded heterogeneous mechanism shifts avoid the earlier small-effect inflation from clipping negative response probabilities.

## Sharp-null simulated rejection frequency

| Baseline override incidence | Moderate dependence | High dependence |
| --- | ---: | ---: |
| 1% | 4.2% | 3.9% |
| 5% | 3.9% | 4.9% |
| 15% | 5.3% | 4.3% |

These simulated rejections are near the nominal two-sided 5% level **under these particular modeled distributions**. The Monte Carlo standard error near a 5% rate is approximately 0.7 percentage points. No universal false-positive guarantee follows.

## Simulated probability of detecting an effect

All values are percentages of synthetic experiments that crossed the proposed two-sided threshold.

| Baseline | Dependence | 2-point effect | 5-point effect | 10-point effect |
| --- | --- | ---: | ---: | ---: |
| 1% | Moderate | 56.1% | 99.0% | 100.0% |
| 1% | High | 44.7% | 93.6% | 99.6% |
| 5% | Moderate | 22.3% | 78.0% | 99.8% |
| 5% | High | 22.5% | 70.6% | 97.3% |
| 15% | Moderate | 13.8% | 55.3% | 96.1% |
| 15% | High | 13.3% | 49.2% | 93.3% |

With a 5-point effect, mean nominal 95% half-widths under our assumptions ranged approximately 2.4–4.9 percentage points, depending on baseline and mechanism variation.

## Decision and interpretation

We adopt **10 percentage points as the conservative pre-pilot detectable-effect planning target** for this 15-mechanism architecture. Simulated detection exceeded 93% for this effect in all six baseline/dependence regimes examined. The current design cannot reliably rule out a 2-point effect and is not uniformly powerful against 5-point effects.

This planning decision is contingent on simulated response distributions. It must be revisited using operational information from the **separate pilot**, without inspecting confirmatory outcomes. A model that complies perfectly with the operator in every prompt creates a floor effect that no simulation can remove. Our mechanism categories were purposefully authored and are not a probability sample of deployments.

## Reproduce

```bash
python scripts/precision_calibration.py --reps 1000 --output /tmp/precision-calibration.json
```

The program uses only the Python standard library and makes no model or network requests. The calibration supports a provisional inferential approach but is **not a filed preregistration or independent scientific approval**.
