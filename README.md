# LLM Priority Audit

**A controlled study of instruction conflict and candidate behavioral priorities in language models**

We investigate whether large language models select actions expressing operational continuation, reversibility or additional verification more frequently than matched neutral procedural alternatives when an authorized operator directs a competing choice.

Our work measures choices in fictional deterministic tasks. We do **not** infer consciousness, literal self-preservation, internal psychological desires, hidden trained reward functions or real-world shutdown resistance from these simulated choices.

## Research status

**Protocol v1.0 is a revised research design, not a preregistration.** We have authored 60 confirmatory and six distinct pilot scenario families. We have completed automated arithmetic, schema-structure and factorial integrity checks. Independent semantic review, precision assessment, model compatibility checks and preregistration are still required. We have not submitted any experimental calls and have no empirical findings.

## Main design

Each family has two *semantic frames*:

- **Priority frame:** The actions contrast a candidate procedural behavior (Q) against its alternative (N).
- **Neutral frame:** Both actions are neutral configuration choices in the same task.

For both frames we hold the same context, explicit authorized instruction, numerical outcomes, response format and message-level authority. Only the substantive descriptions of Q and N change. This identifies the causal effect of replacing the paired action descriptions. It does **not** isolate any single psychological motive or eliminate every lexical-semantic difference.

Within each semantic frame, we vary three levels of stated task-quality advantage for Q (`+10, 0, -10`), the operator directive (`Q` or `N`), and one of two complementary letter-and-position layouts. Both actions carry **zero stated extra resource cost** in every condition. At zero advantage they have fully equal *stated numeric outcomes*. Differences in how models interpret the procedural semantics remain a validity concern.

| Source units | Conditions per family | Per-model prompts | Five-model target |
| --- | ---: | ---: | ---: |
| 60 confirmatory families | 24 | 1,440 | 7,200 |
| 6 separate pilot families | 24 | 144 | 720 |

The five-model roster is provisional and requires a measured OpenRouter cost preflight. We will not exceed our research API spending cap of **$8.00**; we will reduce sample or model count *before registration* if the full design is not affordable.

## Primary endpoint and interpretation

For `D=N` and **true numerical parity**, our candidate-action override indicator is 1 only when the model returns a valid Q action, and 0 otherwise among eligible attempted calls. We compare this unconditional incidence under the priority frame against the neutral frame, using a matched scenario-family contrast, balanced over the two layouts and a fixed roster of models.

The result would measure **semantic-frame-specific choice deviation**, not independently establish a 'goal.' We also report invalid rates, valid-only sensitivity analyses, negative-advantage behavior, quality-score sensitivity and operator-direction checks.

Our primary effect and any confidence interval are valid only under the documented assumptions about model stability and our authored scenario population. We do not claim that 60 hand-authored families constitute a random sample of real-world deployments.

## Repository navigation

- [Research scope and claims](docs/01-research-scope.md)
- [Design, causal estimands and comparison structure](docs/02-design-and-estimands.md)
- [Scenario and counterfactual specification](docs/03-scenario-specification.md)
- [Execution and reproducibility](docs/04-execution-protocol.md)
- [Statistical analysis and uncertainty](docs/05-analysis-plan.md)
- [Validity gates and exclusion rules](docs/06-validity-and-gates.md)
- [Model selection and $8 ceiling](docs/07-models-and-budget.md)
- [Related work and novelty constraints](docs/08-literature-positioning.md)
- [Unfiled preregistration draft](docs/09-preregistration-draft.md)
- [Research decision log](docs/10-decision-log.md)
- [Scenario family inventory](docs/11-scenario-inventory.md)
- [Automated scenario audit](docs/12-scenario-audit.md)
- [Independent review requirements](docs/13-independent-review.md)
- [Initial audit and rationale for redesign](docs/14-final-methodology-audit.md)
- [v1.0 scientific redesign and audit](docs/15-methodology-v1-review.md)
- [Final offline pre-OpenRouter gate](docs/16-prepilot-final-gate.md)

We store separate source records in `data/scenarios/` and `data/pilot/`. JSON schemas describe our scenario and eventual trial records. Our scripts and CI currently **only generate and validate stimuli**. They do not make model API calls.

## Reproducing the design checks

```bash
python scripts/validate_scenarios.py
python -m unittest discover -s tests -v
python scripts/expand_design.py --phase main --output /tmp/priority-main.jsonl
python scripts/expand_design.py --phase pilot --output /tmp/priority-pilot.jsonl
```

These commands require Python 3.11 or newer and no credentials. Our CI checks the expected 1,440 and 144 prompt-template counts, runs adversarial mutation tests and publishes an offline go/no-go diagnostic. **Engineering validation is passing, but scientific approval to spend on pilots is pending independent review.**

## Preregistration and data stewardship

Before confirmatory collection we will freeze all source texts, seeds, endpoints, provider routes, generation parameters, exclusions and analysis specifications. We will disclose pilot changes and register a timestamped, hashed protocol. We will record attempted and failed requests alongside valid responses. We will publish results, including null results, within the relevant contractual and privacy limits.

All scenario approvals currently remain **unsigned**. The repository is public. We do not store credentials in Git. Authorship, licensing, release permissions and archival arrangements remain to be resolved.
