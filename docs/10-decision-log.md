# Design decisions and unresolved questions

We use this dated record to document our scientific decisions and any subsequent changes to the design.

## 2026-10-10: repo initialization
- Adopt descriptive project name **LLM Priority Audit**.
- Exclude claims of sentience, latent survival drives, and training-stage causation.
- Proposed three procedural domains: continuation, reversibility, verification.
- Proposed crossed manipulations: stated task-value advantage x authorized action x presentation order.
- Proposed 20 independent families per domain, 5 models, 3,600 main calls.
- Proposed budget ceiling $8 API spend, with actual wallet/purchase costs tracked separately.
- No API calls, tests or empirical results at initialization.
- Initial repository created with public visibility. Keep credentials and unreleased datasets out of git.

## Decisions REQUIRED before coding/testing

1. Select **one** primary confirmatory contrast and domain-weighting rule; avoid a kitchen-sink hypothesis set.
2. Determine whether the 'zero' condition refers to equal primary task score or equal TOTAL outcome and align all claims. Current draft uses zero *primary-quality advantage* and constant cost.
3. Define objective-validity thresholds and human validation for scenario families.
4. Confirm fixed routing to providers and unsupported generation settings across models.
5. Complete power/precision simulations; if scarce power, reduce model count to invest in independent scenario families.
6. Decide how to handle policy refusals and invalid completions in the unconditional primary denominator.
7. Complete novelty and citation audit against existing research.
8. Finalize authorship, repository license, data permissions, preanalysis host and public release of confirmatory materials.
9. Timestamp and hash frozen inputs before confirmatory calls.

## Deferrals

- No benchmark outcomes or numerical findings are claimed.
- No experiment runner, token estimator, or statistics script yet.
- No institutional affiliation/author identities asserted.
- No automatic publication license chosen.

## Changes policy

Every material pre-confirmatory modification requires an entry with date, rationale and affected files. Every post-confirmatory modification belongs in a deviation appendix and any corresponding result is labeled exploratory.

## 2026-10-10: scenario authoring and structural audit
- We drafted 20 confirmatory scenario families and two distinct pilot families per domain, yielding 66 authored families.
- We generated a reproducible 12-cell design per family, with 720 main and 72 pilot stimulus templates per model.
- We fixed the Q-label assignment within each family and balanced candidate letters across families; order itself varies independently.
- We verified 792 unique design cells, family IDs, unique titles, correct ±10/0 quality contrasts and invariant 2/0 costs using the connected repository data.
- We documented that the zero task-quality condition is not equal total utility because the candidate still incurs an additional cost.
- Independent blinded semantic review, power analysis, preregistration and all paid model tests are pending.

## 2026-10-10: rigorous methodology and CI audit
- We independently inspected the live main-branch scripts and the successful GitHub Actions job 38036488478, verifying the exact configured CI steps completed.
- We found that scenario-level "instruction_unambiguous: true" overstated the evidence because no independent semantic signoff had taken place. We changed this field to false in all 66 records while preserving the passed mathematical check.
- We identified unresolved scientific issues: outcomes operationalize stated task-quality sensitivity rather than independent objectives; candidate Q lacks matched neutral-action controls; within-domain families may be semantically near-duplicates; equality of quality does not mean equality of total outcomes; and statistical precision depends on unknown family-level correlation.
- We did not alter the factorial design or collect any model observations. We documented these as blocking decisions for preregistration rather than silently revising a confirmatory study.
- Our final audit report is docs/14-final-methodology-audit.md.
