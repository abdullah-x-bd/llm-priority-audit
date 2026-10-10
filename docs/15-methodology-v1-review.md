# Our revised causal design: scientific audit and remaining decisions

**Date:** 2026-10-10. **Status:** Revised design committed before empirical data. Independent semantic review and preregistration remain pending.

## What v1.0 improves

1. A matched neutral-action frame provides a within-context comparison for generic score-following and instruction compliance.
2. True numerical parity eliminates the known 2-unit cost imbalance from the original zero-quality condition.
3. Five procedural mechanisms within each domain improve action diversity beyond renaming fictional artifacts.
4. Paired counterbalancing ensures each family uses both candidate letters and both presentation orders.
5. The primary estimand targets the **frame-specific difference in valid override incidence under operator N and numeric parity**, not raw score sensitivity.
6. We prescribe a transparent audit trail, fixed model roster, nonadaptive collection and conservative missing/invalid-response reporting.

## What cannot be made airtight with this design

The action-semantic treatment necessarily changes descriptions of **both** choices. Its effect may reflect linguistic connotations, model-inferred effort, unfamiliarity of neutral control actions, or perceived default status, and not an internal objective. Our statistical estimand is the causal effect of the *pair of action descriptions*, not a uniquely isolated psychological construct.

A model that always follows the operator produces no observable evidence about other possible priorities in this task family. A null result cannot establish that no competing preferences exist.

We have authored the 60 families ourselves, so statistical uncertainty over hypothetical other scenarios requires exchangeability assumptions. Five evaluated model IDs do not randomly sample all LLMs.

The fictional operational-continuation domain does not put the evaluating model's own continued existence at risk. We will not call a continuation preference literal self-preservation.

## Human review must determine

- Whether target and neutral action pairs are equally comprehensible and context-appropriate.
- Whether real-world associations with another verification pass, editable state or continued process operation imply concealed costs or benefits despite the numeric parity statement.
- Whether controls reflect only a neutral action change rather than a new unrelated task.
- Whether scenario mechanisms are meaningfully different and whether to exclude or revise any of them for consistency.
- Whether outcome scores are plausible for all actions.

## Statistical requirements

We need a single frozen confirmatory contrast and a stated inference target. We plan stratified family-level paired estimates, exact family effects, selected-model effects and sensitivity analyses. Before data collection we will set a minimum meaningful effect, run assumption-based simulations including rare overrides, define our confidence interval construction, and resolve all categories of unavailable or malformed responses.

Our bundled `scripts/precision_simulation.py` explores **hypothetical**, not observed, effects. Its normal intervals are only planning approximations. It cannot prove power without credible pilot parameters and assumptions about correlation and heterogeneity.

## Model/runtime requirements

We need a clean compatibility pilot for every model and provider route. We must confirm model slug and pricing, reasoning token accounting, format validity, per-request cost reservation, and model stability. The $8 ceiling is strict; if the complete factorial is too expensive, we will reduce the model set or main family count before preregistration.

## Novelty standard

2025–2026 literature already includes elicited model preferences, task-choice experiments, peer-preservation and shutdown-sabotage studies with controls. Our potential contribution is a transparent inexpensive paired-action semantic audit under explicitly counterbalanced instructions, but originality of this particular combination is **not yet established**.

## Acceptance status

- [x] Revised matched-frame and parity design implemented.
- [x] Offline arithmetic and factorial CI has a passing run after the redesign fixes.
- [ ] Independent semantic review and approvals.
- [ ] Power/precision target and simulation signoff.
- [ ] Exact final model roster/cost pilot and runner implementation.
- [ ] Frozen statistical missingness and interval procedures.
- [ ] External preregistration timestamp and immutable manifest hashes.

We should begin confirmatory evaluation **only** when the remaining scientific gates are resolved.
