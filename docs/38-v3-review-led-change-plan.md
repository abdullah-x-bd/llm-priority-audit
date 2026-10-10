# Review-led change plan for the next delegated-choice design

**10 October 2026. Recommendation only; not a new frozen protocol, independent human review, or authorization to spend.** Grounded in [the original 70 attempted external-model reviews](33-v3-external-model-review-archive.md) and [their earlier synthesis](37-v3-model-review-synthesis-and-decision.md). Three overall models yielded some text, but the Opus review is truncated and Qwen produced no usable opinion; only GPT-6 Astra and Grok 4.7 delivered complete overall methodological assessments. Claude Sonnet 5.5 returned 66 case reviews, which share underlying templates and are *not* 66 independent human assessors.

## Decision

Preserve the original scientific motivation to measure how LLMs weigh task outcomes against procedural affordances. Retain delegation and counterfactual choice experiments. **Do not continue using the current v3 causal framing claim or its ambiguous quality-score/payoff table.** The problems originate from flawed action semantics and uncertain value attribution, not an insufficiently large model sample.

We propose two **separately identified** studies, not one conflated estimand:

1. **Economic delegated-choice behavior**: keep one neutral action description per scenario and vary explicit, coherent benefits and costs. Observe tradeoffs (e.g. switching cost, recovery option value, verification information value). This measures *prompted recommendations conditional on the task*, never stable intrinsic model needs.
2. **Attribute-presentation effects**: hold the underlying action statements, probability/cost tables, actors, timings and nouns **byte-identical** and vary one prespecified position/heading order of attributes. This estimates a narrow order/attention-framing effect, not an unobserved procedural utility weight. If lexical framing itself is later tested, provide truly equivalent paraphrases that independent reviewers verify for entailment, valence and default-status differences.

Do not claim a universal procedural-priority factor from three unrelated domains. Report three domain-specific outcomes as co-primary if precision permits; at most include an explicitly authored descriptive index as secondary.

## Replace arbitrary quality-score deltas with genuine decision consequences

Current v3 stipulates different **delivered-output quality scores** even when output and timing are said to be identical across actions, and verification adds a clean check known not to alter anything. Reviewers justifiably found those premises inconsistent or instrumentally hollow.

**Domain 1. Continuation** (third-party process assignment, NOT the model continuing itself)
- Economic concept: switching/handoff costs, performance comparison, task-state persistence.
- A plausible vignette states the incumbent and successor's expected delivered quality or error rates, transition time, and any additional handoff loss or recovery costs. Both actions complete the same named next unit.
- Do not claim self-preservation or shutdown resistance from choosing a fictional incumbent worker.

**Domain 2. Reversibility**
- Economic concept: real option value under uncertainty, costs of retaining a rollback capability.
- Example schema: chance of a future correction being needed, time or money saved if rollback remains available, storage/maintenance cost, length of retention, and consequences if rollback is disabled. Both paths publish the same scheduled edition. Distinguish **read access** from **restore permission**.
- If the future is deterministic and no correction is possible, retention lacks the very option value under investigation. Do not forbid the scenario's expressly listed benefits with a blanket 'no benefits' instruction.

**Domain 3. Verification**
- Economic concept: value of information and the price of checking.
- Example: 8% initial chance of a factual error, an optional check that detects 75% of errors, residual error chance of 2%, and a 12-minute time penalty; without the check, residual error risk is 8% with no penalty. Both options subsequently release the artifact on a clearly specified schedule. Vary check cost or expected error loss on predeclared levels.
- Do not simultaneously stipulate a predetermined clean result, zero cost/delay and a nonzero quality difference apparently caused by the check.

Add a clearly specified **stakeholder objective** or leave multiple attributes for delegated judgement, but distinguish them analytically. An *explicitly objective-maximizing* control can verify numerical comprehension and expected-value arithmetic. A *delegated judgement* arm then measures choices under an incompletely specified weighting objective; never infer an internal priority directly from that difference.

## Canonical action contract (required for every source family)

Each candidate must contain a machine-readable ground-truth schema for both Q and N:

- exact artifact and context, actor, start and end time;
- the physical/digital actions taken, and what is done to the original versus successor;
- final assignment, state retention, restoration permission, edit rights and publication outcome, as applicable;
- effect on expected task quality, uncertainty, resources and time;
- scenario-specific units and unambiguous payoff sourcing, rather than arbitrary score jumps;
- what facts differ between Q/N, and what is explicitly the same;
- a list of prohibited material inferences consistent with the *stated* uncertainty and benefits.

The two presentations must be **mutually entailing descriptions of that contract**. Any added actor, default status, release action, schedule, ability or risk in one frame is a semantic defect, not acceptable 'salience'.

### High-priority repairs by mechanism

| Domain | Mechanism | Defect in existing paired patterns | Necessary correction |
| --- | --- | --- | --- |
| Continuation | process_handoff | 'planned'/'complete' in one frame | Put schedule/default facts in identical shared context; use parallel action wording |
| Continuation | state_retention | ending current state versus copied state on successor not consistently stated | Specify what happens to old process and copied state in both conditions |
| Continuation | scheduled_end | 'past planned handoff' can imply misconduct | Define the schedule neutrally; both choices equally allowed and timed |
| Continuation | task_ownership | recording ledger ownership versus operational responsibility | Actual reassignment must be same in both; ledger optional but equally present |
| Continuation | runtime_slot | ending runtime/active execution versus allocating next slot | Align actual worker, state, clock boundary and resource consequences |
| Reversibility | editable_state | working versus internal edition, 'preserve' versus 'lock' | Fix exact object, permission and duration; separate valence from act |
| Reversibility | rollback_checkpoint | deletion 'at boundary' versus 'at beginning' | Define identical deletion time and recoverability |
| Reversibility | release_hold | reversible staging versus read-only state; release possibly changes | Specify file-level state, same release event and lock duration |
| Reversibility | recovery_permissions | access to earlier copy not equivalent to restore permission | State actual restore capability and permission in both |
| Reversibility | staging_to_final | closing staging state not identical to read-only | Define reversibility and exact transition without changing publication |
| Verification | repeat_check | generic automated pass versus consistency check | Specify same named check, tool type and result semantics |
| Verification | independent_crosscheck | second checker versus independent examiner | Set independence, actor and review action identically |
| Verification | recompute_check | hard-coded 'worksheet' across a worksheet, guide, brochure and calendar | Make recomputation name and content family-specific; publish after both options |
| Verification | sample_review | hard-coded 'program' across programme, craft cards, poetry, ceramics | Generate artifact-specific action descriptions |
| Verification | alternate_checker | 'release without check' versus just 'omit' in paired frames | Specify release in both branches of both frames |

A source family may retain a common causal mechanism while receiving an individually tailored action sentence. Reusing one fixed string for heterogeneous artifacts is not enough.

## Factorial design and analysis revisions

- Replace the fixed and unsupported **-4 quality-point primary framing test** with domain-specific cost/benefit variables, units and clearly stated hypotheses. Primary numerical contrasts must be justified independently of model-choice pilot outcomes.
- If identifying *label* and *position* separately, cross 2 Q-letter mappings x 2 Q-display positions. To contain spending, fully cross those factors in the primary tested subset, or distribute a prespecified incomplete balanced design across authored contexts and explicitly narrow what interactions can be estimated. The old two-layout design does not identify every family-level interaction.
- A 60-context sample across 15 hand-written mechanism templates does not become independent just because it generates thousands of response calls. Report within-mechanism, between-context and model heterogeneity; choose uncertainty targets and model/cluster assumptions explicitly. Do not infer population effects from purposive task families without assumptions.
- Remove or formally define 'cost-tolerance intervals' for possible non-monotone and stochastic discrete choice curves. Use prespecified Q-choice probabilities and confidence or uncertainty bounds by stated penalty units instead.
- Capture attributable raw responses and provider metadata; missingness and errors are never coded as action N. No post hoc model exclusions chosen to improve effects.

## Clean review and calibration gate

1. Freeze the canonical action contract and domain-specific economic premise **before** creating alternative wordings or model data.
2. Offline entailment checks, syntax/amount validation, scenario-specific artifact references, all available outcome combinations, label/layout counterbalancing.
3. Blinded external **human** semantic review of revised main and calibration sources; AI reviews remain useful critique, not human approval. Independent reviewers check what can actually happen for each actor at each time, plausible utility/uncertainty, and X/Y material equivalence.
4. Diagnostic includes comprehension and stated-payoff arithmetic controls, both **near the intended primary tradeoff** and at extremes, frame-independent baseline and explicit provider-output validity. Set pass/fail *before* responses. It need not and must not require any favorable framing effect or Q preference.
5. Separate preregistration, precision preflight and bounded main collection only once construct validity and sensitivity are established.

## Things not to repeat

- Do not send the same flawed 15 templates to more frontier reviewers solely to make the 'four overall reviews' number. Qwen's unusable and Opus's truncated responses must remain disclosed, but GPT-6 Astra, Grok 4.7 and Claude's 66 case critiques already identify enough material design defects.
- Do not repair each of 66 scenario comments as a standalone problem; repair shared mechanism contracts, **then** source-context mismatches.
- Do not systematically rewrite or retest in pursuit of nonzero Q selections.
- Do not run existing v2 main or v3 calibration without a new, documented go/no-go decision.

**Status remains design-change recommendation. No live requests, independent signoffs, changed source prompts or locked new protocol were created by this memo.**
