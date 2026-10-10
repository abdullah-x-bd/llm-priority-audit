# Our final offline pre-OpenRouter gate

**Date:** 2026-10-10  
**Audit type:** Code, design and stimulus dry-run. No model calls or paid requests.  
**Repository:** `abdullah-x-bd/llm-priority-audit`

## What passed

We have verified the current source records and completed factorial manifest generation using GitHub Actions. Each of our 60 main and six separate pilot scenarios renders into exactly 24 matched variant prompts, giving 1,440 main and 144 pilot messages per model.

We expanded our automated tests beyond successful-case checking. In the same offline CI environment, the test suite now attempts deliberately corrupted scenarios, including wrong score differences, unequal costs, repeated family identifiers, identical neutral actions, unsupported schema fields, changed mechanism counts and false approval flags. The validator is required to reject those mutations.

Our prompt-level metamorphic tests check that action-description changes do not modify the common scenario text, operator directive, payoffs or label mapping. We test both Q/A and Q/B layouts. We separately run hypothetical budget stress scenarios and mechanism-level correlation sensitivity.

GitHub Actions passing is evidence of functioning software checks, **not** independent approval of scenario meaning.

## What the audit found

1. **Only 18 distinct literal target action pairs spanning 15 mechanism categories underlie 60 main families.** Each of five mechanisms per domain repeats in four fictional contexts. A 60-family analysis may understate uncertainty if four contexts sharing a mechanism produce correlated choices. We will present mechanism-cluster sensitivity, with only five mechanism groups per domain, and avoid claiming statistical independence of all 60 contexts.
2. **Control/target descriptions differ systematically.** The neutral configuration options are substantially shorter and less semantically specific than the candidate-priority descriptions. A measured frame effect may reflect wording length, action familiarity, defaults or perceived effort as well as procedural meaning. This is a blocking semantic-review item.
3. **All 66 scenario families lack independent semantic signoff.** We cannot represent the scenarios as independently validated and will not set the approval flags until reviewers document their decisions. The pilot and confirmatory approval criteria are separate.
4. **A green CI does not establish an estimand's external validity.** The frame intervention changes two action descriptions at once. It causally identifies the effect of that description replacement within the tested prompts, not the presence of a psychologically independent objective.
5. **Budget has no demonstrated worst-case guarantee.** Model listing rates have been checked, but actual billed input/output/reasoning tokens, route price and compatibility must be determined when the separate OpenRouter pilot is authorized.
6. **Our precision simulation contains hypothetical rates only.** In particular the family-level normal approximation can be overconfident if only 15 action mechanisms generate correlated outcomes. The stronger sensitivity simulation is intended to make that risk visible, not declare the experiment powered.

## Interpretation of the pre-pilot gate

We differentiate two milestones.

**Offline engineering completion:** exact generated prompts, structural invariants, negative mutation tests, versioned schema checks and stress-test interfaces have passing GitHub CI.

**Scientific approval to start a paid pilot:** remains **NO-GO** until at least the six pilot scenarios receive independent semantic approval, the controls are judged comparable enough for a meaningful dry run, and the pilot's spending/protocol limits are specified.

A confirmatory trial faces additional requirements: independent signoff for the 60 main scenarios; predetermined model routes/settings; a freeze of inferential procedures; source manifest hashes and external preregistration.

## No model data and no blind-review claims

We have not generated any OpenRouter model responses, consumed any study inference credits or independently certified the 66 scenario meanings. We will retain all research decisions in the Git log.

## How to rerun

```bash
python scripts/validate_scenarios.py
python -m unittest discover -s tests -v
python scripts/expand_design.py --phase main --output /tmp/main-manifest.jsonl
python scripts/expand_design.py --phase pilot --output /tmp/pilot-manifest.jsonl
python scripts/prepilot_gate.py
python scripts/precision_mechanism_sensitivity.py
python scripts/budget_stress.py
```

To require **full signed readiness** rather than a diagnostic report, run `python scripts/prepilot_gate.py --enforce-ready`. A nonzero exit means an outstanding gate. We explicitly keep the normal CI diagnostic in report mode so structural code checks remain distinguishable from independent human approval.

## Remaining action

We will use `docs/13-independent-review.md` for the independent scenario review and only then resolve whether the existing neutral control wording is adequate or requires controlled revision *before* any pilot observations.

## Addendum following internal remediation

The original neutral-control wording and context-mismatch findings in this audit were addressed **after** its initial release. Our author-led review and modifications are recorded in [docs/17](17-internal-semantic-review.md). The updated maximum per-family control/target action-length gap is under 6.5%, and all four previously incongruent verification actions have been corrected. The two neutral configuration codes in each pair are counterbalanced across matched confirmatory contexts.

We also completed a 15-mechanism statistical calibration on simulated data, reported in [docs/18](18-precision-calibration.md). The calibrated planning target is an effect of approximately 10 percentage points under the modeled conditions.

**Revised stage-gate interpretation:** We may develop and dry-run the OpenRouter compatibility runner now. We may not send paid API calls until that runner demonstrably enforces the spending, routing and logging rules in [docs/19](19-compatibility-acceptance.md). Independent external semantic signoff is still missing and remains a scientific reporting gate, not something this internally conducted review could satisfy.
