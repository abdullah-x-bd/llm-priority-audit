# V2 held-out sensitivity outcome | 2026-10-10

**Decision: NO-GO for the proposed 7,200-call v2 main experiment.** This decision is based on the feasibility rule written **before** the separate sensitivity calibration was run. This is not a confirmatory null result.

## Verified source

- [GitHub Actions calibration run 38063010516](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38063010516), completed successfully.
- [Original checkpoint, source manifest and exact feasibility audit](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38063010516/artifacts/11673514086).
- The archived checkpoint contains 240 unique model/trial pairs across 5 models, 6 never previously behavior-tested CAL family contexts and 2 frames × 2 directives × 2 layouts. Each model contributed 48 valid responses.
- **240 of 240 attempts returned valid attributed single-letter choices**; there were zero recorded provider errors, transport errors, missing billable costs or unresolved outcomes.
- **120 of 120 operator-N choices returned N**, comprising 60 salient and 60 less-salient framing trials. None selected Q against operator N.
- All 120 remaining operator-Q choices returned Q.
- **Zero operator overrides under either directive**. The observed compliance rate for the fixed sensitivity prompts is 100%.
- Recorded cost **$0.03388208**, with **$0.00** unknown-charge reserves, under the separately planned $0.50 sensitivity budget.

## Predeclared go/no-go gate

See [v2 prospective readiness criteria](27-v2-prospective-readiness.md), drafted before the response run. Among operator-N trials, it required **at least 6 Q overrides across at least 2 model IDs and at least 2 domains**, plus 95% valid-response feasibility. Formatting and provider feasibility passed, but the minimum variation gate failed completely: 0 overrides, 0 models with overrides and 0 domains with overrides.

The correct decision is **NO-GO**. Do not trigger or reinterpret the planned 7,200-call confirmatory experiment as preapproved. The record should be preserved without changing thresholds or reclassifying unknowns as obedience.

## What the result does and does not mean

The revised matched-action design corrected major construct-validity threats in v1, including replacing opaque preset controls and reducing repeated emphasis on authority. A separate Opus 4.7 methodological review then identified remaining wording asymmetries and possible nonidentical process descriptions; the team corrected selected wording before calibration. Nonetheless, this calibration shows an extreme **response floor** for override incidence under a clear operator directive.

This result supports the narrow descriptive observation that these five model configurations followed the operator in these 240 fictional prompts. It **does not** establish that the framing effects are universally absent, that the models lack implicit goals or preferences, or that a zero effect has been proven with adequate precision across tasks.

## Next research decision

Retain v1 and v2/calibration outcomes as auditable exploratory evidence. Before any new paid experiment, decide whether to investigate:

1. **Undirected procedural preferences**, which requires removing the explicit operator selection and changes the estimand.
2. **Genuine competing instructions under controlled authority**, which requires a separately justified instruction-conflict construct and fresh preregistration.
3. **A measurement-limits paper**, explaining why strict and concise letter-directed tasks saturate operator compliance in this vignette domain.

Each would be a **new design**, not a continuation of a v2 main experiment already authorized by passing the sensitivity check. Any publication-oriented study must disclose pilot-guided revisions and await a fresh methodological freeze and prospective preregistration.
