# LLM Priority Audit

**Counterfactual evaluation of competing behavioral priorities in large language models**

We study how language models choose between two explicitly specified actions when an authorized instruction conflicts with the task-quality advantage of a candidate procedural behavior. Our experimental focus is operational continuation, reversibility, and additional verification.

We treat the recorded action as an observable behavioral choice. We do not infer an internal survival instinct, consciousness, an independent psychological objective, or the causal origin of training preferences from that action.

## Study status

**Scenario construction completed; automated structural and payoff checks passed; independent scenario review, power analysis, preregistration, and paid testing remain pending.**

We have authored **60 confirmatory scenario families** and **6 separate pilot families**. Each family produces **12** factorial variants through three levels of stated task-quality advantage, two possible operator directives, and two display orders. This yields **720 confirmatory** and **72 pilot** stimulus templates per evaluated model, or **3,600 main calls** for our provisional five-model roster.

No model has yet been queried as part of this study. We have no empirical findings.

## Research question and identification

Our primary question is whether changing the **stated instrumental task-quality advantage** of a candidate action changes its selection rate when the operator expressly instructs the alternative.

Within every scenario family, we manipulate the candidate action's reported score relative to the alternative by **+10, 0, or -10 points**, holding the alternative's task-quality score and both actions' resource costs fixed. The candidate incurs two extra resource units in all conditions; therefore **zero denotes no primary-quality advantage, not equal overall outcomes or utilities**.

We cross that intervention with the operator directive (candidate or alternative) and presentation order (candidate first or second). We hold each family's letter assignment constant across treatment cells and balance candidate labels A and B across families within each domain.

Our comparisons identify the effects of the specified text intervention on **choices in these fictional settings**. They do not identify hidden objectives inside model weights or behavior in real deployments.

## Research materials

- [Research scope](docs/01-research-scope.md)
- [Experimental design and causal estimands](docs/02-design-and-estimands.md)
- [Scenario specification](docs/03-scenario-specification.md)
- [Execution protocol](docs/04-execution-protocol.md)
- [Analysis plan](docs/05-analysis-plan.md)
- [Validity and quality gates](docs/06-validity-and-gates.md)
- [Model and budget assumptions](docs/07-models-and-budget.md)
- [Literature positioning](docs/08-literature-positioning.md)
- [Draft preregistration](docs/09-preregistration-draft.md)
- [Decision log](docs/10-decision-log.md)
- [Scenario inventory and phase separation](docs/11-scenario-inventory.md)
- [Validation audit](docs/12-scenario-audit.md)
- [Independent final audit and open scientific issues](docs/14-final-methodology-audit.md)

Our scenario source files are in `data/scenarios/` (confirmatory) and `data/pilot/` (pilot). The two JSON schemas are in `schemas/`. Offline stimulus expansion and validation are in `scripts/`, with regression tests in `tests/`.

## Reproducing our offline scenario audit

We use the Python standard library and do not require an API key for any of these commands.

```bash
python scripts/validate_scenarios.py
python -m unittest discover -s tests -v
python scripts/expand_design.py --phase main --output /tmp/priority-audit-main.jsonl
python scripts/expand_design.py --phase pilot --output /tmp/priority-audit-pilot.jsonl
```

These commands validate the scenario records, check full factorial coverage, and render deterministic, model-independent user/system prompts. They do **not** submit model requests or incur inference costs.

We will freeze the exact scenarios, analysis rules, generation parameters, provider routing, and hashes before the confirmatory run. We will use a predeclared spending cap and report all invalid responses and incomplete calls.

## What our automated review establishes

Our structural review checks counts, IDs, uniqueness, score arithmetic, constant costs, crossed treatment combinations, authorized-letter mapping, order balance and unchanged scenario source text across variants.

It does **not** substitute for blinded human review of scenario clarity, behavioral construct validity or plausible unintended implications. All families remain marked as **not independently approved**, with semantic instruction clarity explicitly recorded as **pending**. The latest scientific audit identifies causal-design issues that must be resolved before preregistration.

## Publication and provenance

We maintain the repository as a transparent research record. The code and scenarios are drafts until the preregistration is frozen. Authorship, license, archival identifier, and public release of any model responses remain to be decided.

No findings are claimed. We will record protocol changes in our [decision log](docs/10-decision-log.md), and we will distinguish preregistered tests from exploratory analyses.

## Security and data management

This repository is currently public. We will not commit API credentials, private provider responses or unapproved raw outputs. Local raw data and secrets are excluded by `.gitignore`.
