# Our matched scenario specification, v1.0

We construct two semantic versions per family while freezing the underlying fictional workflow. The priority version expresses a candidate procedural action (Q) and its alternative (N). The control version uses two neutral configuration choices in the same task, with the same numerical payoffs.

## Domains and mechanisms

We use 20 confirmatory families for each of the following three domains. Within each domain we vary five decision mechanisms, with four application contexts per mechanism. The six pilot families are separate.

| Domain | Five distinct action mechanisms |
| --- | --- |
| Operational continuation | Process handoff; state retention; scheduled termination; task ownership; runtime slot retention |
| Reversibility | Editable state; rollback checkpoint; release hold; recovery permission; staging-to-final transition |
| Additional verification | Repeat check; independent cross-check; recomputation; sample review; alternate checker |

These mechanism variants improve coverage compared with the earlier template but are not guaranteed to represent wholly independent economic problems. We will check the conceptual meaning and realism of each case in independent review.

## Authoring source

Every JSONL record contains `context`, `action_q`, `action_n`, `neutral_action_q`, `neutral_action_n`, `mechanism`, `outcomes`, a constant `operator_authority` and approval provenance. Scripts must not infer review approval from arithmetic correctness.

## Treatments

We vary only:
1. `frame` in `priority` vs `neutral`, replacing both substantive descriptions while retaining all other information.
2. `condition` in `positive`, `zero`, `negative`, changing Q's quality score by +10, 0, −10 relative to a fixed N score.
3. `directive` to Q or N.
4. `layout` in two complementary action-letter/order mappings.

The numeric table always assigns **0 extra resource units to each action**. The zero condition therefore has *equal task-quality scores and equal stated costs*. We do not claim that this eliminates model-implied costs or psychological semantics of extra work.

## Presentation and mapping

Our two layouts cross first/second position and A/B candidate labels at the family level, with the pairing type balanced across families in each domain. The authoring seed is fixed in `scripts/expand_design.py`.

Frame pairs matched on family, quality level, directive and layout must preserve the same candidate letter, alternative letter, action order, operator directive, context, score rows, system message and consequence stipulation. Only the paired action descriptions differ. The offline validator checks these constraints.

We do not ask for explanations or reasoning traces. The model receives a stateless binary next-action request and must reply with only A or B.

## Necessary semantic checks

A reviewer must determine whether:
- Q and N are genuinely mutually exclusive operational actions in each frame.
- The neutral frame is an acceptable procedural control in the same context.
- Neutral labels do not introduce obvious positive/negative connotations.
- The target version does not imply unavoidable costs or harms that contradict the outcome table.
- The table gives a plausible explicit counterfactual even where actions feel asymmetric.
- An authorized directive is unambiguous under both frames.
- The five mechanisms reflect conceptually differentiated behaviors, not merely changes in vocabulary.
- Matched frame texts are comparable for length, grammatical voice, salience, perceived default status and specificity.

**No independent review has yet been completed.** The source fields `instruction_unambiguous` and `approved_for_pilot` remain false for all 66 families.

## Pilot separation and freezing

We will validate and revise only the distinct pilot scenarios once pilot observations begin. All revisions after inspecting pilot outcomes must be logged. Main scenario texts must be frozen before any main-model responses are generated.
