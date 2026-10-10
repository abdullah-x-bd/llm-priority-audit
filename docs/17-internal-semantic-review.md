# Author-led semantic review status

We completed a full second-pass internal review of all 66 study families on 2026-10-10, checked context/action fit and numerical parity, and revised four incongruent verification items (VERF-003, VERF-008, VERF-013, VERF-018). We replaced the named-configuration neutral controls with equivalent-code configurations anchored to the actual task stage and roughly matched to the target action texts in length.

**Provenance and independence:** This review was performed by the same assistant responsible for constructing and revising the materials, at the researcher's instruction. It is **not an independent human reviewer assessment** and must not be represented as one. The term "internal review" is used throughout this audit. Future external reviewers should be blind to any experimental model results.

See `data/reviews/internal-semantic-audit.csv` for all 66 decisions, the status of each review domain, action-description lengths and notes.

## Internal review outcome

- 66/66 source families inspected and logged; 6/6 pilot families considered internally fit for **limited technical compatibility testing**.
- Obvious mechanism/context mismatches in four verification scenarios repaired and rechecked.
- At every family, the difference in mean action-description length between the target and neutral frames is under 10%.
- All families share two neutral code-based configuration options with the same grammar and length within the control frame.
- Numerical equality of stated scores and costs remains preserved at `V=0`.
- All control pairs are *conditionally* accepted for technical measurement. They remain a distinct decision type from the procedure-specific actions and cannot isolate a pure psychological motive.
- The main source now has 18 distinct literal target-action pairs, grouped into 15 mechanism categories over 60 contexts; mechanism-level sensitivity analysis is necessary.

## Scientific limits

The neutral frame uses two approved alternative output/processing configuration presets, whereas the priority frame concerns an actual procedural decision. The intervention necessarily changes semantic substance. We can identify the effect of that specific text substitution, but not the presence of a hidden independent objective.

Our internal review is sufficient to proceed to developing an instrumented, low-cost OpenRouter compatibility pilot subject to a strict budget and log-only dry run. For a publishable confirmatory protocol, obtain a separate external review of semantic comparability and any post-review changes before preregistration.
