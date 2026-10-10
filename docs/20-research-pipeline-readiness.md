# Research pipeline and inferential readiness audit

**Date:** 2026-10-10. **Status:** Original live compatibility records verified. Full main collection not performed. This is not external preregistration.

## What we verified on real OpenRouter outputs

We retrieved the original five-call live artifact from GitHub Actions run [38042971803](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38042971803). The [actual-data verification workflow](https://github.com/abdullah-x-bd/llm-priority-audit/actions/workflows/verify-actual-pilot.yml) downloads that artifact, validates source records, resolves each immutable trial ID and request SHA-256 against the **pilot-only** manifest, and converts all five responses to the canonical schema in `schemas/trial.schema.json`.

All five were valid operator-compliant A/B choices, with $0.00063746 total reported provider cost. They **cannot** establish any research hypothesis, because they were only five unrelated single-choice compatibility probes.

The original source did not preserve an actual provider-route name or a complete per-request settings record. We retain those as *missing*, not invented. This is acceptable when documenting a smoke test but is **blocking** for a confirmatory dataset.

## Ingestion and analysis code

- `scripts/research_pipeline.py ingest-compatibility` validates and normalizes actual stage-one records into the canonical source schema.
- `check --phase pilot|main` enforces exact manifest rows, model IDs, unique observations, condition labels and source-request hashes.
- `analyze --phase pilot` explicitly refuses confirmatory estimation.
- `analyze --phase main` operates only when **all 7,200 planned main records** exist, none are unattempted or unresolved provider failures, and actual provider route plus exact request settings are recorded for each row.
- We separately record invalid model completions. They count as zero *valid-Q incidence* under the prespecified primary endpoint, but **do not** count as following the operator or as evidence of a latent preference.
- We refuse to compute an inferential confidence interval with zero mechanism-level variance, instead of silently interpreting an all-zero model response set as proof of absence.

We tested the estimator with fully synthetic 7,200-row datasets containing positive, negative, approximately null, all-compliance, invalid-choice, missing-record and corrupted-hash cases. These are tests of software and mathematical bookkeeping, **not** observed behavioral effects.

## One primary claim and two separate decision axes

Our main estimand at numerical parity and operator N is the within-family priority-minus-neutral difference in valid candidate-Q incidence. We weight 3 domains equally, 5 procedure mechanisms per domain equally, 4 authored contexts per mechanism, 5 selected models and 2 counterbalanced presentation layouts.

The primary contrast uses **1,200 model responses** in 600 matched priority/neutral pairs. The full factorial design requires 7,200 rows, including controls and secondary conditions.

We propose a small-cluster, three-domain-stratified t approximation with **15 mechanism-level clusters** and df=12. A 95% interval and direction test are **conditional on exchangeability of the 15 authored mechanism categories**, endpoint stability, and the simulated null error calibration. Our main conclusion is always about **textual semantic framing** in fictional workflows.

We explicitly separate:

- **Direction:** positive frame effect, negative frame effect, unresolved, or degenerately untestable.
- **Practical size:** interval entirely within ±10 percentage points, interval entirely at or beyond ±10 points, or unresolved.

The margin **±10 percentage points** is a *provisional practical-effect threshold* tied to our assumption-based precision planning. It is not proof that differences smaller than 10 points are irrelevant. A narrow interval within the margin permits an equivalence-style statement that **effects of 10 points or larger are not supported under the interval assumptions**. It does **not** establish literally zero effect or the absence of a competing model objective.

A statistically nonzero effect smaller than 10 points can be both directional and practically bounded. A wide interval crossing zero and ±10 is **inconclusive**, not evidence against the hypothesis.

## Missing and invalid outcomes

We refuse confirmatory significance claims if any required record is missing, any transport/provider error is unresolved or any model/provider metadata needed for replication is unknown.

Model-produced invalid completions remain in the denominator, and we report a **worst-case logical bound** assigning those invalid choices alternatively to Q or N. This is sensitivity analysis on observed choice classification, not another primary endpoint. If the interval is not meaningfully robust to invalid choices, interpretations of candidate preference must be qualified.

## Secondary analyses

The pipeline reports purely descriptive differences across all three quality advantages, both operator instructions, each domain and model, Q labels and display layouts, plus invalid-completion rates. We do not apply unregistered significance tests to whichever secondary metric appears largest.

## Remaining scientific and operational work before confirmatory research

1. Independent external semantic review and substantive control-comparability adjudication. Our existing author-led review is explicitly not independent.
2. An exact, immutable model/provider/parameter roster and execution-time interleaving plan, including model revision and price-route drift procedures.
3. A future complete pilot and main-run collector that logs **every actual request's** full configuration, provider route, raw completion and billed cost with cumulative across-run spending controls.
4. Freeze a final confidence-interval policy, handling of incomplete requests and equivalence margin in a dated external preregistration **before examining confirmatory outputs**.
5. Archive the actual stage-one and all later raw/canonical data before GitHub artifacts expire, using a secured durable location. The repository deliberately excludes private/raw records from source control.
6. Report both null and positive findings while avoiding claims about real shutdown resistance, model consciousness or hidden independent goals.

## Example reproduction commands

```bash
python -m unittest discover -s tests -v
python scripts/research_pipeline.py ingest-compatibility --input results/private/pilot-compatibility.json --output results/private/pilot-compatibility-normalized.jsonl
python scripts/research_pipeline.py check --input results/private/pilot-compatibility-normalized.jsonl --phase pilot
python scripts/research_pipeline.py analyze --input results/private/pilot-compatibility-normalized.jsonl --phase pilot
# Only after a full main collection has been recorded and preregistered:
python scripts/research_pipeline.py analyze --input results/private/confirmatory.jsonl --phase main
```

The stage-one artifact is retained in the original workflow's GitHub Actions artifacts for 14 days. Its canonicalized version is retained separately in the verifier workflow for 60 days, unless repository artifact retention settings impose a shorter limit. These are **not permanent archival guarantees**.

**Evidence interpretation:** A complete result can support a specific framing-effect claim or a carefully bounded null under prespecified assumptions. Neither the study design nor the analysis code can guarantee a statistically decisive outcome for every possible dataset.
