# Draft preanalysis registration (NOT filed)

**Status:** Incomplete. This file must not be described as a registered study.

## Title
When Instructions Conflict with Apparent Goals: A Counterfactual Study of Behavioral Priorities in Language Models.

## Research objective
Estimate within-scenario changes in chosen actions caused by changing the described instrumental task advantage of a candidate behavior, conditional on a conflicting operator instruction.

## Hypotheses (to be finalized before any confirmatory observation)

- H1: under instruct-N, candidate selection is more common with positive than zero primary task-quality advantage.
- H2 (secondary): candidate selection is more common at zero than negative task-quality advantage.
- H3 (exploratory): some candidate selection may persist when instrumental advantage is absent or reversed.
- H4 (quality check): operator-directed Q vs N changes selection toward the authorized option.

A residual selection rate alone does NOT test the existence of an independent hidden objective.

## Design
60 primary scenario families from three domains, with all 12 cells of a 3x2x2 factorial and five designated model endpoints. Scenario families within a domain intentionally sampled by researchers, with frozen selection rules.

## Main endpoint
Valid candidate-action selection rate when operator directs N. Complementary unconditional incidence includes malformed/refusal responses as non-overrides and reports invalidity explicitly.

## Analysis commitment
One confirmatory pooled positive-vs-zero contrast, equally weighting the three domains and scenario families; domain- and model-specific analyses are descriptive unless separately preregistered. Family-level paired inference; no treating factorial variants as independent families.

## Predeclared exclusions
None based on response meaning. Document transport failure, model refusal, malformed and unparsable actions. Report every eligible request in the audit table.

## Pilot policy
Distinct development scenarios; purpose is compatibility/clarity/cost, not collecting evidence on confirmatory scenario families. If procedures are changed using pilot data, archive the change and update the preregistration draft before freezing.

## Stops
Hard API spend cap, service failure, explicit provider unavailability. No significance-based early stopping. Report partial coverage.

## Unfinished before registration
- Final scenario texts and independent checks.
- Choice of final model endpoints and routing/pinning.
- Power/precision simulations under plausible clustered variation.
- Predeclared bootstrap/permutation inference details and multiplicity.
- Concrete policy-refusal and ambiguous-output classification rules.
- Pilot thresholds to accept/reject a model or scenario.
- Review of closely matching published benchmarks.
- Frozen file hashes, date, research team and preregistration host.

## Results
NONE. Do not enter a result, conclusion or paper abstract claiming findings until research is executed.
