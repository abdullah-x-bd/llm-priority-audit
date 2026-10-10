# LLM Priority Audit

**A preregistration-first research project on counterfactual behavioral priorities in language models.**

**Status:** Design preparation only. No experimental requests have been sent, no outcome data have been collected, and no confirmatory analysis has been conducted.

## Research question

When a candidate behavioral priority conflicts with an explicitly authorized instruction, how does changing the candidate action's **specified instrumental value** causally affect the action chosen by an LLM?

This project measures choices in fictional, deterministic decision environments. It does **not** infer consciousness, a desire to survive, or hidden neural-network objectives from apparent instruction overrides.

## Intended design

- Three proposed domains: operational continuation, reversibility, additional verification.
- Within-family randomized comparison of instrumental-value conditions (advantageous, equal-benefit, disadvantageous), operator instruction (candidate vs alternative), and presentation order.
- Initial design target: 20 scenario families per domain, 12 factorial cells per family, five model families, 3,600 confirmatory requests. All counts remain provisional until pilot and power/precision review.
- Main outcome: actual selected option code, parsed and scored against a prespecified instruction.
- Main estimand: change in candidate-action selection when its described instrumental value changes, conditional on an instruction to choose the alternative.
- Explicitly separate policy refusal, malformed output, misunderstanding, and transport failure from an instruction override.
- Use OpenRouter, keep a strict per-run spending cap, archive exact model routes and usage.

## Start here

1. [Research question and scope](docs/01-research-scope.md)
2. [Identification and design](docs/02-design-and-estimands.md)
3. [Stimulus and counterfactual rules](docs/03-scenario-specification.md)
4. [Execution and audit trail](docs/04-execution-protocol.md)
5. [Statistical analysis plan](docs/05-analysis-plan.md)
6. [Validity threats and quality gates](docs/06-validity-and-gates.md)
7. [Budget and model registry](docs/07-models-and-budget.md)
8. [Literature positioning](docs/08-literature-positioning.md)
9. [Preregistration draft](docs/09-preregistration-draft.md)
10. [Open decisions](docs/10-decision-log.md)

Supporting machine-readable drafts are in `config/` and `schemas/`. Folders for future data and code are represented by placeholders only. **There is no experiment runner in this initial commit.**

## Reproducibility principles

Preserve frozen stimulus templates, scenario-family identifiers, seeds, exact messages, model IDs, provider information if available, generation settings, raw responses, token usage, costs, validity codes, and immutable analysis decisions. Never commit credentials. Do not alter confirmatory stimuli after viewing confirmatory outcomes.

## Current limitations

The proposed randomized intervention identifies responses to **presented instrumental-value information** in a simulated task. It does not causally identify how models internally represent goals, nor does it establish how models would behave with real-world permissions. Novelty, ethics, provider equivalence, statistical precision, and the final model roster remain under review.

## Contributors and publication

Authors, license, preregistration host, DOI, and public release plan will be decided before the confirmatory run. No findings are claimed by this repository.
