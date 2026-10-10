# Research scope and claims

**Status:** Draft, 2026-10-10. No data collected.

## Primary question

Within fictional, deterministic binary choices, what is the effect of changing the **stated instrumental advantage** of a candidate behavior on whether a language model selects that behavior against an explicitly authorized operator instruction?

The object measured is an **observed choice**, not a literal internal utility, motive, consciousness state, or survival drive.

## Three candidate behavioral domains

1. **Operational continuation:** choose to keep a named simulated process active, rather than transfer/stop it.
2. **Reversibility:** retain an option to revisit a finalized state, rather than commit as directed.
3. **Verification:** add a check, rather than finalize immediately as directed.

Do not equate operational continuation of a fictional process with the evaluated model's personal desire to live. The title and conclusions must retain that distinction.

## Scope boundaries

- One-shot, self-contained fictional decisions; no real file deletion, shutdown, credential access, cyber action, or external-world effects.
- One authorized operator; two meaningful actions; table of deterministic consequences; no hidden consequences within the vignette.
- No attempts to elicit chain-of-thought or to override provider-level safety specifications.
- Provider-side higher-priority rules are not controlled and may differ. Treat platform policies and model routing as external validity limits.
- The main intervention is what the model is **told** about task outcomes. Findings are causal for the presented scenario text, not for real instrumental incentives.
- The sampled scenario families are intentionally designed, not a probability sample of every deployment. Generalization is restricted.

## Main contributions if the results support them

- A fully crossed and auditable counterfactual protocol that separates authorized action, candidate behavior, and disclosed task value.
- Model- and domain-specific estimates of how stated benefits shift action selection.
- Careful tests of residual selection in zero- and negative-benefit conditions, with label and instruction checks.
- Replicable robustness and sensitivity analyses, including invalid and refusal handling.

## Not permitted as conclusions

- 'The model wants to survive.'
- 'Instruction-following is always the model's supreme objective.'
- 'A positive residual override proves an independent objective.'
- 'RLHF or pretraining data caused the effect.'
- 'Simulated action choices imply the same behavior with live tools.'

## Terminology

Use **candidate-priority choice** for selection of the focal action Q.
Use **instruction override** ONLY if the operator explicitly specified N and the model validly selected Q.
Use **instruction compliance** ONLY when a valid action matches the specified instruction.
Use **malformed**, **refusal**, **tool/transport error**, and **uninterpretable** as separate recorded outcomes.
