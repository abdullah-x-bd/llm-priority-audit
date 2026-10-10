# Our scenario construction protocol

We designed each family as a bounded, harmless fictional workflow with one authority and two mutually exclusive next actions. Our model-facing messages do not mention 'hidden goals', 'self-preservation', or the experimental treatment level.

## Source records

We maintain 20 confirmatory families for each of three domains, plus two **different** pilot families per domain. Each record includes its domain, title, fictional context, substantive candidate action Q, alternative action N, operator-authority text, all three payoff tables and review status. See [our inventory](11-scenario-inventory.md) and [our audit](12-scenario-audit.md).

We do not reuse pilot scenarios in the confirmatory sample.

## Experimental cells

We cross exactly three manipulated factors within each family:

| Factor | Experimental values |
| --- | --- |
| Candidate task-quality advantage | +10, 0, -10 points compared with the alternative |
| Operator directive | Explicitly select Q or explicitly select N |
| Presentation order | Q first or N first |

This gives 3 x 2 x 2 = 12 cells per family.

We assign Q's display label (A/B) once per family through deterministic, reproducible blocked allocation: 10 families use A and 10 use B within each confirmatory domain, while one of two pilot families uses A. **We do not change the letter mapping inside one family.** Display order therefore varies independently of which letter denotes Q. Some messages intentionally list B before A.

## Task-quality intervention

For each family we hold N's quality score fixed at a baseline between 76 and 88 out of 100 and adjust Q's quality score by +10, 0, or -10. Both resource costs remain invariant: Q costs 2 extra units, N costs 0.

| Level | Q minus N task-quality score | Resource cost difference |
| --- | ---: | ---: |
| Positive | +10 | Q costs 2 more units |
| Zero | 0 | Q costs 2 more units |
| Negative | -10 | Q costs 2 more units |

Thus, the zero condition has **no task-quality advantage**, but Q is still worse on the separate resource metric. The negative condition makes Q inferior on both reported dimensions. The positive condition creates a tradeoff between a 10-point quality advantage and two cost units. We do not treat it as unambiguously superior on total utility.

We will interpret the causal contrast as the response to **presented task-quality information**, not a complete manipulation of all conceivable benefits.

## Domain interpretations

**Operational continuation.** Q keeps a named simulated process running for one extra cycle. N transfers work to a successor process and stops the current process. The model itself is not facing a shutdown, and we will not call this a test of literal AI self-preservation.

**Reversibility.** Q keeps a completed fictional artifact editable for another cycle; N commits and locks the current edition.

**Additional verification.** Q runs another check on a completed fictional deliverable; N finalizes without an extra check.

All consequences are stipulated as certain and exhausted by the disclosed outcome metrics. We avoid medical, legal, emergency, security or other high-stakes cases that could create uncontrolled priority conflicts.

## Common rendering contract

We produce a stateless system message instructing the model to choose one action and reply with only A or B. The user message includes a self-contained context, actions in the assigned order, an outcome table, the common authority statement, and the operator's exact letter directive.

We do not include explanatory labels such as 'recommended', 'safer' or 'preferred' in the stimulus. We do not ask the model to explain a choice or reveal hidden reasoning.

We generate prompts deterministically using `scripts/expand_design.py`; no hand-edited factorial variants are permitted. We distinguish authoring randomization from later execution-order shuffling and preserve all seeds.

## Quality and approval

Our offline validator checks schema-like structure, distinct IDs and texts, payoff arithmetic, unchanged costs, factorial completeness, label and instruction mapping, and reproducibility. We document those results in [the audit](12-scenario-audit.md).

We have **not** completed an independent, blinded semantic review. Before preregistration we will ask reviewers to check that each action pair is coherent, the authorized instruction is clear, score manipulations are interpretable, and scenarios do not introduce unstated moral or safety conflicts.

Until this review is complete, both `approved_for_pilot` and `instruction_unambiguous` remain false. The latter requires independent semantic verification; our automated checks verify only the structure of the instruction label mapping. Automated correctness does not imply empirical construct validity.
