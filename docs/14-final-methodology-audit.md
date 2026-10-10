# Our initial audit and rationale for redesign

We audited the first, 12-cell version of LLM Priority Audit on 2026-10-10. Its initial GitHub automated checks passed, but we identified scientific problems that were not solved by arithmetic consistency.

The original design changed task-quality scores without a neutral procedural comparison. Equal quality still imposed a higher fixed resource cost on the candidate action. Many scenarios changed only fictional artifacts rather than the mechanism of the choice. The analysis lacked a frozen primary estimand and a realistic precision calculation.

These were **blocking** limitations for any assertion that the experiment isolated a competing behavioral priority.

## Changes adopted in v1.0 before data collection

We added a paired neutral semantic frame, standardized equal resource costs, diversified within-domain procedural mechanisms, crossed directives and balanced letter/order layouts, and changed the primary comparison to priority-versus-neutral at full stated numeric parity.

We also corrected previously overclaimed instruction-clarity metadata. The updated flags explicitly record that independent reviewers have **not** approved the scenarios.

This audit remains a historical record, not evidence that the revised design has solved all construct-validity problems. The current [v1.0 audit](15-methodology-v1-review.md) specifies remaining limitations and pre-registration gates.

## Historical technical evidence

The initial GitHub Actions run completed successfully at https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38036488478 .

Our conclusions must always distinguish successful offline engineering tests from independently validated causal mechanisms.
