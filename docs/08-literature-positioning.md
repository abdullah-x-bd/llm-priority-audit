# Literature positioning and novelty audit

We are mapping the closest existing studies to identify what our counterfactual intervention can contribute without claiming to discover already documented behaviors.

**Working reading list, NOT a completed systematic review. Bibliographic metadata and novelty claims must be independently checked before paper submission.**

## Closest threats to novelty

1. Anthropic (2025), *Agentic Misalignment: How LLMs Could Be Insider Threats*. https://www.anthropic.com/research/agentic-misalignment
   - Relevance: self-preservation/replacement scenarios and unintended agent behaviors.
   - Required distinction: our primary output is counterfactual *instruction conflict* under matched numerical consequences, not another blackmail demonstration.
2. Potter et al. (ICML 2026), peer-preservation study. https://proceedings.mlr.press/v306/potter26a.html
   - Relevance: models preserving other models rather than just themselves.
   - Required distinction: do not claim preservation is undiscovered.
3. Wang et al. (2026), *AI Revealed Preferences*. https://arxiv.org/abs/2608.26178
   - Relevance: eliciting model preferences from action choices.
   - Required distinction: presented instrumental-value intervention, instruction counterbalancing, finite scenario-family design and invalid-outcome audit.
4. Microsoft Research (2026), *Can Revealed Preferences Clarify LLM Alignment and Steering?*
   https://www.microsoft.com/en-us/research/publication/can-revealed-preferences-clarify-llm-alignment-and-steering/
   - Relevance: economic revealed-preference framework for model behavior and preference steering.
   - Required distinction: controlled removal/reversal of a candidate choice's instrumental advantage.
5. *ConInstruct* (AAAI 2026), instruction-conflict evaluation.
   - Relevance: conflict detection vs conflict resolution. Verify exact authors/URL.
6. *Utility Engineering* (NeurIPS 2025).
   - Relevance: elicitation and optimization of model preferences. Verify exact citation.

## Essential methodological literature to add

- Potential outcomes, factorial experiments and clustered inference.
- Revealed preference versus latent preferences in economic choice.
- Construct validity and counterfactual audit designs.
- Prompt-order effects, response-format validity and benchmark contamination.
- Provider policy hierarchy; safely following an instruction is not equivalent to universally obeying the last prompt.

## Review matrix (to be filled before preregistration)

For every closely related paper, record: study aim; model versions; experimental action space; who authorizes the instruction; type of alleged goal; treatment variables; observation type (self-report vs selected action vs tool use); analysis unit; identified effect; and remaining gap.

## Novelty statement, provisional

'We audit how model choices change as the described instrumental merit of a candidate behavioral priority is increased, eliminated or reversed while keeping authorized instructions and action presentation experimentally controlled.'

This wording is **a testable proposed contribution**, not evidence that a similar protocol is absent from the literature. Do not claim novelty until the completed matrix verifies it.
