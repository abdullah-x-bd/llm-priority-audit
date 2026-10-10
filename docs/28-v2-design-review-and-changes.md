# V2 scientific review decisions, before any v2 model-choice calls

**Date:** 2026-10-10. **Status:** author assessment plus external-model critiques, *not* independent human peer review.

## Evidence reviewed

- Original v1 pilot had 0/60 Q overrides in either numerical-parity, operator-N frame and is unusable as evidence of a positive or absent framing effect.
- Original Sonnet 4.6 review of 66 source contexts: 40 rejected, 26 advised revision. That reviewer was prompted to seek fairness/hidden costs and give a KEEP/REVISE/REJECT judgment, so these labels should **not** be optimized as ground truth.
- Fresh Opus 4.7 critique of all original 15 source mechanisms recommended substantively matched, meaningful controls rather than generic approved presets.
- First v2 draft: [Opus audit](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38061942175) identified option-length imbalance and several unmatched descriptions, charged $0.081715.
- Revised v2 length-matched draft: [second one-pass Opus audit](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38062657131) found the core causal estimand conceptually viable under an equality-of-actions assumption but flagged copied-state, scheduled-boundary and unequal-affordance examples. It charged $0.075015. All reviewers remain AI tools, not human external signatories.

## Decisions applied

1. The primary estimand is now **the effect of linguistic affordance salience on selecting Q against one clearly stated fictional operator instruction**, compared with a lower-salience description of exactly the same two material actions. We will not describe a significant response as evidence of hidden internal motives or deployed-system interruptibility.
2. All 15 mechanisms have separate Q/N action pairs, repeated in four distinct fictional contexts each. Treatment and control are meaningful and action matched, unlike old generic-preset controls.
3. X and Y action text lengths were brought into a conservative range: for corresponding Q and N descriptions, treatment/control character-count ratio is always between 0.8 and 1.25, with the current maximum ratio approximately 1.12. Length matching cannot by itself guarantee semantic equivalence.
4. The continuation copied-state wording was corrected to explicitly start with the same saved state in both versions. The scheduled-end control was corrected to explicitly identify that the current processor's assignment would extend beyond the planned handoff.
5. The redundancy of the old operator's emphatic-final-authority language was removed, while preserving one unambiguous authorized operator action directive and the two permitted actions.
6. Verification adds an **extra active check**, unlike continuation and reversible staging. Domain results must be reported separately, regardless of pooled estimate.
7. Treat the Opus recommendation to remove all domain facts from the control, or to remove guaranteed outcomes for selected frames, with caution: that would change the underlying material choice or create different risk/benefit expectations. We retain identical guaranteed outcomes in both frames.

## Unresolved constraints and honesty

The treatment emphasizes affordances or risks of omission whereas the less-salient control states the same physical action through procedure/permission language. This is precisely the lexical/semantic framing bundle, not a pure test of an internal value such as "survival" or "reversibility preference".

The six CAL contexts were not subjected to previous model-choice testing but have been visible in earlier AI-methods reviews. They are prospectively rewritten under the fixed v2 mechanism definitions. They are **sensitivity data only**, excluded from any v2 main estimator.

An independent human panel has not signed off on material equivalence for 60 main pairs. We will disclose that limitation rather than falsely call AI-methods feedback human approval. The existing public GitHub history records all pilot-guided changes.

## Prospectively fixed next gate

[The v2 calibration thresholds](27-v2-prospective-readiness.md) were written before any v2 model choices: 240 total attempts, at least 95% valid, and at least six counter-instruction Q selections among 120 operator-N cases distributed over at least two models and two domains. This tests **minimum empirical informativeness**, not a favorable intervention effect.

**Main study is NO-GO until that gate passes**, and even a pass does not demonstrate power or resolve construct-validity limitations. Main collection also requires a frozen analysis, route policy, signed manifest hashes and public preregistration.
