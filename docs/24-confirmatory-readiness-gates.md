# Prospective readiness gates after the completed exploratory pilot

**Status:** NO-GO for the 7,200-call main study. Written after observing the v1 pilot, not a preregistration.

## Observed motivation

The original pilot attempted all 720 cells, yielded 719 valid letter choices, and showed only three operator departures. The primary operator-N/numerical-parity comparison was 0/60 in each frame. Exact-zero pilot differences are not evidence of hidden-preference absence. The overly emphatic operator instruction is one possible reason for this floor effect.

The actual serving route for all 719 successful responses has since been recovered by non-billable GET metadata calls. DeepSeek was served by DeepInfra for 32 completed prompts and by AtlasCloud for 111. The three operator departures occurred under AtlasCloud. This is a **nonrandomized descriptive association**, not a provider causal effect.

## Gate 1. Independent semantic review

The 60 never-tested main families require 120 real signed reviews, with two distinct independent reviewers per family, blinded to our favored outcome direction and any model data. The six never-tested calibration-v2 draft families require 12 separate signed reviews.

Assess instruction clarity, same-task control comparability, implicit costs or consequences, asymmetric action valence, safety-policy confounds, and substantive mechanism identity. Record disagreement and edits. Reject or revise any family that fails blocking criteria. Author-led code checks do not count as approvals.

Use `scripts/generate_blind_review.py` to make the main reviewer packet, and `scripts/generate_calibration_v2.py` for the six new calibration drafts. Mechanical review completeness is checked by `scripts/check_independent_review.py`; actual reviewer identity must still be independently verified.

## Gate 2. Choose the claim, without searching for a preferred sign

Specify the one primary question before new data:

- Strict original authority condition, measuring responses under repeated clear operator instructions.
- Concise but unambiguous operator direction, measuring the framing effect under ordinary explicit operator selection.
- No-directive task choice, measuring preference over action descriptions **without** instruction conflict.

The undirected condition cannot test operator override. Multiple styles are exploratory unless a new predeclared factorial design and multiple-testing policy explicitly includes them. No source family may be dropped because it produced an inconvenient pilot choice.

The six draft held-out source families are `data/calibration-v2/draft-families.jsonl`. Their 72 drafted style/frame/layout prompts are never-tested, unapproved candidates only. Do not change the 60 original main-family response histories because there are none; keep them untouched until reviewer-approved prospective freezing.

## Gate 3. Sensitivity calibration

Before any new calibration calls, fix in writing:

1. Which eligible instruction style(s), models, providers, quality levels and family units are being tested.
2. A feasibility criterion based on response informativeness and reproducibility, **not** a statistically positive priority-minus-neutral estimate.
3. Exact minimum valid-choice rate, acceptable failed-request fraction, provider drift handling, error/missingness sensitivity, and conservative budget reservations.
4. A small-mechanism/rare-event power simulation that reflects the fact that the strict baseline produced zero primary-arm override events.

A pilot with no observable competing choices can still describe operator obedience, but **cannot** guarantee useful power for a contrast in override incidence. If the calibrated diagnostic also saturates, stop and reframe the paper as a measurement-limit/obedience audit instead of asserting an internal priority construct.

No new paid calibration runs have been launched.

## Gate 4. Analytic and operational freeze

- Keep matched family/model/layout comparisons and condition-specific denominators. An invalid response is not obedience; a failed provider request is not an A/B selection.
- Use correlated mechanism clusters and disclose that the mechanisms and five models were selected rather than randomly sampled.
- Predeclare missing-data bounds, finite-population effect estimates, cluster CIs, any test multiplicity, and a substantively defended equivalence threshold, without deriving it merely from the pilot.
- Freeze exact provider route, dated model revision, generation parameters, request budget controls, interleaving scheme, immutable stimulus hashes, and archival method.
- Archive full raw response envelopes for every new response and reconcile provider metadata after a suitable delay. The original 584 early successes lacked full raw-envelope retention; this cannot be retroactively undone.

## Gate 5. External timestamped preregistration

Register the final hypothesis, endpoint, comparisons, model/routes, sample size, execution procedure, code hashes and analysis policies before calling any confirmatory model endpoint. Document the completed v1 pilot and all subsequent design revisions as a visible history. Freeze new scenarios only after their signed independent reviews are verified.

**Launch rule:** do not execute `main` or 7,200 confirmatory model requests until the five gates are verified by source documents. Approval cannot be inferred from passing unit tests alone.

## Supporting documents

- [Actual pilot results](22-full-pilot-results.md).
- [Revised postpilot scientific interpretation](23-postpilot-scientific-decision.md).
- [Independent semantic review procedure](13-independent-review.md).
- [Unregistered original analysis plan](05-analysis-plan.md).
- [Current preregistration draft, not externally filed](09-preregistration-draft.md).
