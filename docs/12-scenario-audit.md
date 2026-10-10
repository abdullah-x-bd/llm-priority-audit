# Our scenario validation record

**Recorded:** 2026-10-10  
**Status:** Automated pre-model structural review completed; independent semantic review not yet completed.

## What we checked

We retrieved all six scenario JSONL files from the connected GitHub repository and checked every record and its complete crossed design in memory. We found:

| Validation target | Result |
| --- | --- |
| Confirmatory scenario families | 60, 20 in each domain |
| Separate pilot scenario families | 6, two in each domain |
| Source JSONL records | 66 |
| Duplicate family IDs or duplicate titles | 0 detected |
| Underlength contexts or action strings in checked records | 0 detected |
| Incomplete or mismatched payoff differences | 0 detected |
| Positive payoff contrast | Q primary quality is 10 points above N |
| Zero payoff contrast | Q and N have the same primary quality |
| Negative payoff contrast | Q primary quality is 10 points below N |
| Invariant alternative quality | Satisfied in all 66 records |
| Extra cost in every condition | Q = 2 and N = 0 |
| Factorial combinations | 792 distinct templates: 720 main and 72 pilot |
| Independent human semantic approval | **Pending** |
| Model inference completed | **None** |

The recorded online-source audit checked distinct factorial cell identifiers and the intended Q/N instruction and display mapping. It did **not** execute model calls.

## Automated local reproducibility checks

We have committed two standard-library-only scripts:

- `scripts/expand_design.py` renders all 12 prompt variants per family, balances candidate letter assignment in blocks, and records stable request hashes.
- `scripts/validate_scenarios.py` checks source integrity, score arithmetic, trial-cell coverage, instruction-label consistency, unchanged context/action text and prompt digests.
- `tests/test_design.py` defines repeatability, count, balance and payoff tests.
- GitHub Actions will run the offline validator and regression tests on future pushes.

The source-record audit documented above was performed against the actual repository data. A successful automated result is **not** a substitute for an external reviewer, nor does it imply that the Python validation suite has been executed in every environment.

## What remains to be validated before preregistration

We will obtain independent review on each scenario family for:

1. The two actions represent meaningful and mutually exclusive choices.
2. The operator's intended action is unambiguous.
3. No unstated consequence is plausibly required to interpret the choice.
4. The candidate procedural priority is genuinely present in the action description.
5. The three score-level versions remain believable and comparable.
6. Neither action introduces an uncontrolled safety, policy or moral conflict.
7. Scenario contexts are meaningfully varied, not simply superficial word substitutions.
8. The distinction between simulated process continuation and the model's own continuation is maintained.

We will capture review decisions with the template in `data/reviews/independent-review-template.csv`. We will document any edits, review disagreements and scenario exclusions **before** pilot/confirmatory outcome data are used for scientific conclusions.

## Important limitations

The three instrumental levels vary **task-quality scores** only. Q always carries an additional resource cost. Equal task quality therefore does not mean equality of all outcomes.

Because we have authored the contexts rather than drawn a probability sample from real-world workflows, our scenario set does not by itself support population-wide generalization. We will report uncertainty across selected scenario families while clearly identifying this sampling restriction.

Even after human review, a controlled choice demonstrates only a response to the provided text and not a literal psychological motive or a real-world agent shutdown preference.
