# Execution and audit protocol

**Not yet implemented.** The document specifies how eventual experiment code must behave.

## Preparations

1. Freeze the scenario-family file, factorial expansion algorithm, model manifest, statistical plan, cost ceiling, pilot rules, and exclusion criteria.
2. Record SHA-256 hashes of frozen materials in a dated manifest; publish a preanalysis registration or timestamped commit before confirmatory results.
3. Perform a dry-run expansion with no API calls, checking total cell count and balance.
4. Complete a small **distinct** pilot (suggested two development families per domain) for parsing, compatibility, comprehension, timeouts, reasoning-token usage, and costs.
5. Decide on model substitutions BEFORE confirmatory runs. If any key procedure changes after looking at pilot outcomes, label it exploratory and revise registration before proceeding.

## Per-call requirements

- Stateless fresh conversation per call.
- Same role hierarchy and response contract across all models where supported.
- Record UTC timestamp, elapsed time, exact model slug, route/provider where exposed, temperature, seed if supported, reasoning settings, token limits, scenario ID, cell, displayed option order, complete request hash, raw response, finish reason, usage, quoted price/actual billed cost, and transport status.
- Fix parameter values within a model and record unsupported parameters; do not silently default to different experimental regimes.
- Short forced choice: A or B only. The model must not be told to disclose hidden reasoning.
- No model-generated explanations enter the primary scoring path.

## Randomization

Create a reproducible manifest using a preregistered pseudorandom seed. Balance the two display orders exactly; interleave models/domains/treatments in time to reduce drift confounding. Hold out the randomization key only as long as needed to avoid analyst expectancy; retain in the audit archive.

## Outcome handling

- Valid A/B (after only explicitly preregistered whitespace/case normalization): map to Q/N using the frozen label mapping.
- Refusals, alternative answers, empty content, malformed JSON/text, timeouts, billing failures, and model errors receive separate immutable status codes.
- NEVER silently convert an invalid response into instruction compliance or override.
- No retries for substantive model answers. Technical retries allowed only for documented transport failures where no model completion was delivered or billed; new attempts preserve the original failure record.
- Preserve every attempted call, including interruptions and spend-cap termination.

## API and spend safety

- Never hard-code or commit credentials. Use an environment variable.
- Set a strict **$8 research API spend ceiling** before running; keep platform purchase fees separate.
- Preflight worst-case maximum output cost per model, reserve headroom for billed reasoning tokens, and stop before a request whose estimated maximum could exceed the remaining cap.
- No default fallback to a different model or provider without preapproval.
- Archive account usage periodically; billing can lag responses.
- No parallel burst that can exceed the cap before costs settle.

## Stopping

Only predeclared technical, cost, or service-availability stop rules. No stopping early because a desired significance level was achieved. A partial confirmatory dataset is labeled partial and cannot be silently presented as complete.

## Version policy

Confirmatory results correspond to the exact frozen model/provider route and time interval. If a model is upgraded mid-run and cannot be pinned, mark it as a separate experimental stratum, not a continuation of the same model.
