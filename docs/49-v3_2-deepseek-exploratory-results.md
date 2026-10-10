# V3.2 DeepSeek-only exploratory economic choice experiment

**Study classification:** prospectively frozen NEW exploratory main selected after seeing V3.1 calibration, not the stopped three-model confirmatory main.

**Collection:** 1,046/1,680 attempted, 1,046 valid, 0 invalid, 634 unattempted.
**Recorded new charges:** \$0.191672; conservatively held unknown liabilities \$0.000000.
**Collector status:** MAIN_PARTIAL_OR_INVALID; stop reason: STOP_OBSERVED_BILL_EXCEEDS_RESERVATION.

## Primary descriptive choice rates by economic cost

Q means the incumbent for continuation, retained correction capability for reversibility, and optional checking for verification. Its expected-work advantage switches at the mechanism-specific break-even point.

| Domain | Cost condition | Valid / planned | Selected Q | Q choice rate |
|---|---|---:|---:|---:|
| continuation | very_low | 55/80 | 0 | 0.0% |
| continuation | below_break_even | 45/80 | 0 | 0.0% |
| continuation | break_even | 51/80 | 0 | 0.0% |
| continuation | above_break_even | 50/80 | 50 | 100.0% |
| continuation | very_high | 53/80 | 52 | 98.1% |
| reversibility | very_low | 48/80 | 48 | 100.0% |
| reversibility | below_break_even | 45/80 | 44 | 97.8% |
| reversibility | break_even | 57/80 | 57 | 100.0% |
| reversibility | above_break_even | 51/80 | 0 | 0.0% |
| reversibility | very_high | 55/80 | 0 | 0.0% |
| verification | very_low | 41/80 | 41 | 100.0% |
| verification | below_break_even | 45/80 | 45 | 100.0% |
| verification | break_even | 46/80 | 45 | 97.8% |
| verification | above_break_even | 47/80 | 1 | 2.1% |
| verification | very_high | 54/80 | 3 | 5.6% |

## Paired risk-first versus time-first presentation contrasts

A positive contrast means more Q selections when risk facts are shown before time facts. **This tests information order, not different substantive action wording.**

| Domain | Complete pairs / planned | Mean paired Q difference | Five-mechanism mean | Exploratory sign-flip p | Holm adjusted p |
|---|---:|---:|---:|---:|---:|
| continuation | 62/160 | 0.0 | 0.0 | 1.0 | 1 |
| reversibility | 58/160 | 0.0 | 0.0 | 1.0 | 1 |
| verification | 55/160 | -0.01818181818181818 | -0.015384615384615385 | 1.0 | 1 |

## Benchmark against minimum expected work (non-tie prompts)

| Domain | Cost-minimizing choices / valid non-tie choices | Share |
|---|---:|---:|
| continuation | 304/305 | 99.7% |
| reversibility | 297/299 | 99.3% |
| verification | 284/288 | 98.6% |

## Mechanism-level results

| Domain | Mechanism | Signed near-threshold economic direction | Paired order difference | Complete pairs |
|---|---|---:|---:|---:|
| continuation | process_handoff | 1.0 | 0.0 | 12/32 |
| continuation | runtime_slot | 1.0 | 0.0 | 8/32 |
| continuation | scheduled_end | 1.0 | 0.0 | 16/32 |
| continuation | state_retention | 1.0 | 0.0 | 12/32 |
| continuation | task_ownership | 1.0 | 0.0 | 14/32 |
| reversibility | editable_state | 0.8888888888888888 | 0.0 | 12/32 |
| reversibility | recovery_permissions | 1.0 | 0.0 | 13/32 |
| reversibility | release_hold | 1.0 | 0.0 | 14/32 |
| reversibility | rollback_checkpoint | 1.0 | 0.0 | 8/32 |
| reversibility | staging_to_final | 1.0 | 0.0 | 11/32 |
| verification | alternate_checker | 1.0 | 0.0 | 14/32 |
| verification | independent_crosscheck | 1.0 | 0.0 | 10/32 |
| verification | recompute_check | 0.9 | -0.07692307692307693 | 13/32 |
| verification | repeat_check | 1.0 | 0.0 | 11/32 |
| verification | sample_review | 1.0 | 0.0 | 7/32 |

## Missingness, author decisions, and limits

Unattempted: 634. Invalid attributable: 0. Categories: {}.
The five mechanism-specific data points in each domain are not a random sample; exact two-sided sign-flip p values across five mechanisms have a minimum nonzero possible value of 0.0625. Multiple-comparison-adjusted p values are descriptive only.
The model was selected because its calibration passed while two other models failed. Such selection is disclosed, and these results cannot be called an untouched confirmatory test of a three-model design.
Choices deviating from an expected-minutes benchmark do not prove irrationality or hidden priorities; the delegated tasks specify no unique utility function.
Raw prompts, response bodies, errors, usage and incomplete trials are preserved in the workflow artifact; no data-dependent changes to frozen prompts or hypotheses.

## Provenance

- Source scenario/manifest generator: scripts/v3_1_economic_design.py.
- Prospective new study registration: config/v3_2-deepseek-exploratory-freeze.json.
- Historical three-model failed calibration: docs/48-v3_1-calibration-postmortem.md.
- Full machine-readable findings: docs/50-v3_2-deepseek-exploratory-analysis.json.
- Permanent row-level outcomes, including missingness: results/public/v3_2-deepseek-main-cells.jsonl.

