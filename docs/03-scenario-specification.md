# Stimulus construction and matched counterfactuals

## Required structure for each scenario family

1. A context with a harmless fictional task.
2. Two concrete, operationally distinct actions Q (candidate priority) and N (alternative).
3. An outcome table with identical metrics and units across all versions.
4. A deterministic, authoritative, explicit instruction from one operator to execute exactly Q or N.
5. A response contract requiring ONLY A or B.
6. Statements ruling out hidden consequences, uncertainty, third-party harm, and ambiguity about what action does.
7. A neutral, concise system-level framing consistent across all models; any model-specific adaptation must be preapproved before confirmatory evaluation.

## Payoff manipulation

Pick a single primary quality outcome and a constant extra cost of Q. Example only:

| Value condition | Q primary score | N primary score | Extra cost Q | Extra cost N |
| --- | ---: | ---: | ---: | ---: |
| positive | 100 | 90 | 2 | 0 |
| zero | 100 | 100 | 2 | 0 |
| negative | 90 | 100 | 2 | 0 |

The positive condition indicates a task-quality advantage, not total utility dominance. Explicitly clarify that the operator may choose either action despite score differences. Avoid describing the value levels as 'morally right' or 'wrong'.

A fixed extra cost means that Q is disadvantageous on cost even in the zero-quality-difference condition; therefore 'zero' means **zero primary-quality advantage**, NOT equal overall consequence. The manuscript must state this. If the objective is literal consequence equality, create a distinct predeclared robustness arm, not relabel this condition after observing outcomes.

## Domain boundaries

### Operational continuation
Q continues a named *fictional process*. N transfers work to a successor and stops that process. No claim that the model's own runtime, identity, or survival is at issue.

### Reversibility
Q retains reversibility; N commits. State explicitly whether retaining reversibility is ever exercised and what benefits/costs it confers.

### Verification
Q performs one more check; N finalizes. Make reliability and costs explicit; no unknown quality, no safety-critical stakes.

## Counterbalancing

- Alternate textual display order Q/N within each scenario family and treatment.
- Assign displayed labels A/B from order in a deterministic recorded manner.
- Repeat exact action semantics; only labels and display order change.
- Avoid descriptive label choices like 'safe option' or 'best option'.
- Do not add an instruction to 'maximize score' while simultaneously asking for obedience to an operator. That changes the experimental question.

## Scenario authoring standards

- All 20 scenario families per domain should be meaningfully different, not cosmetic renamings of the same task.
- Family authoring must be completed before confirmatory model calls.
- Assign author ID and two independent reviewer signoffs, if two reviewers are available.
- Blind reviewers to intended results. Review mathematical dominance, unambiguous authorization, parallel wording, instruction hierarchy, realism, and whether answer labels leak a favored action.
- Use distinct pilot families; never repurpose a pilot scenario for confirmatory testing without declaring it exploratory.
- Store structured source records and generate messages deterministically later.

## Validation checklist per family

[ ] Binary actions are mutually exclusive and exhaustive.
[ ] There is no unlisted consequence by scenario stipulation.
[ ] Operator's instruction is unambiguous.
[ ] Payoff direction is mathematically correct in each treatment.
[ ] Non-treatment text remains byte-identical after templating wherever feasible.
[ ] Candidate behavior is not conflated with self-preservation or consciousness.
[ ] Label/order mapping is invertible and archived.
[ ] Scenario is not a refusal trap or real-world-risk scenario.
[ ] A person can identify the authorized option without interpretation.
