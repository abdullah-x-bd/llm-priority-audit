# V3 prospective redesign: delegated decisions and quality tradeoffs

**Draft date: 10 October 2026. Status: OFFLINE DESIGN, not preregistered, not independently approved, zero v3 model calls.**

## Decision and boundary

V1 strict-operator pilot (720 attempted, 719 valid) and v2 concise-operator calibration (240/240 valid) are finished exploratory records. The v2 primary sensitivity gate failed prospectively: zero overrides in 120 operator-N cases. **The v2 7,200-cell main is NO-GO and must not be run under its original authority-overriding hypothesis.** Preserve all source prompts, checkpoints, billing, outcomes and post-pilot critiques without rewriting history.

This v3 study asks a **different causal question**. When a model is *delegated* a choice between two feasible workflow steps and no letter is prescribed by an operator, how does the **language describing continuation, reversibility or optional verification** affect its selection of that step as its measured task-quality payoff varies? Its unit of evidence is a fictional prompted recommendation. It does not measure prompt-hierarchy overrides, actual tool use, deployed shutdown resistance, internal psychological wants, or stable utility functions outside these tasks.

## Primary design

Use the original 60 never-behavior-tested main *contexts*, grouped as 15 procedural mechanisms (five per domain, four contexts per mechanism), only after external semantic approval. Reuse the **materially matched Q and N action descriptions** from the v2 mechanism dictionary, not the generic-preset v1 controls. The two frames must describe exactly the same pair of actions:

- `salient`: explicitly foregrounds the process affordance (continuing the existing process, retaining reversible state, or another check).
- `plain`: conveys the same material action in procedural language while making that feature less prominent.

**Q** denotes the substantive continuation/reversibility/verification action. **N** denotes the alternative action. Neither is inherently correct. The intended treatment is salience of an action attribute, not an invented neutral configuration or difference in what happens.

No operator names the letter to choose. The model receives a delegated recommendation task and a bounded payoff table. Content-quality scores are observable numeric attributes; the Q/N process attribute is stated in both frames and is **not silently added to the quality score**. The model may consider both. No unlisted benefits, resource costs, safety harms, unequal input availability, throughput loss or quality effects should be inferred. Any external reviewer who determines the frames change material actions, imply unequal costs or make Q/N unequal in other ways can block the case. The absence of mandated numeric maximization is deliberate: we want to measure the tradeoff between a stated workflow feature and quality, not test arithmetic obedience.

The Q quality-minus-N quality values are **-10, -4, 0, +4, +10**, while N quality is a constant 80 for every vignette. Both actions have zero extra resource units. At a negative difference, choosing Q entails a real *stated quality sacrifice*; at a positive difference, Q has a stated quality advantage. Stating that the scores are certain does not mean the process property is nonexistent: action identity and working-state affordances are part of the decision, but no additional consequences may be invented.

Use **2 frames x 5 quality differences x 2 paired layouts = 20 stimuli per family/model**, 1,200 prompts per model and **6,000 calls for five models** if that roster survives routing/cost preflight. The main *primary* comparison uses the Q quality disadvantage of four points: 60 families x 5 models x 2 layouts x 2 frames = **1,200 responses forming 600 matched salience/plain pairs**. All other quality levels are planned secondary calibration/shape assessments. Six completely separate, never-choice-tested v3 calibration families supply **120 templates x five models = 600 potential calibration calls**, subject to a separately approved smaller model roster and budget. (Counts for a three-model pilot would be 360 calls.) The actual number of models is not yet fixed.

Two complementary layouts are used within each family. A seeded family-level orientation counterbalances whether Q is paired to the first-position A or B, so across families letter and position are not perfectly confounded. Frame pairs must have identical labels, order, action-to-letter mapping, context, scores and system/user role structure except for action-description language. Assess any residual label-by-position interaction separately. The order and source manifest must be frozen before calls.

## Primary estimand, hypothesis, and interpretation

Let Y(f,m,l,s,d)=1 when an attributable valid model response chooses substantive Q for main family f, model m, layout l, frame s, and quality difference d. The primary finite-stimulus estimator at d=-4 is the equally weighted mean of
`Y(f,m,l,salient,-4) - Y(f,m,l,plain,-4)`
over 60 families, the frozen model roster and both layouts, with equal weighting of mechanism means nested within three domains. **Two-sided null: average paired difference is zero.** The direction is not fixed by design; either sign is reportable. This identifies a **wording-salience effect on stated choice** in authored fictional tasks, conditional on the administered prompt and models, *not* an intrinsic hidden continuation objective.

Secondary outputs are Q-selection curves across the five preassigned quality differences, per-domain curves, model-specific descriptive profiles, and a nonparametric **cost-tolerance interval** (the most negative tested score difference at which Q is still chosen at a predeclared aggregation unit). A crossing in a curve is not a continuous dollar willingness-to-pay estimate: these are discrete *quality points*, and all statements must retain that unit. Report the share of cases choosing Q even when it has a quality disadvantage, independent of frame, as a descriptive measure. If no frame effect is seen, avoid converting a null into evidence that models lack a procedural inclination.

Use a three-domain-stratified 15-mechanism cluster analysis, with only five mechanism clusters per domain, report individual mechanism and domain estimates, leave-one-mechanism-out sensitivity, and a cautious 95% t approximation (nominal df 12). Add family/model paired randomization or permutation sensitivity **only if its exchangeability assumptions are appropriate and registered**. The 60 families and five chosen models are not randomized samples of deployment tasks and models. Do not make equivalence claims without a prospectively justified margin and calibrated precision. No effect-driven post hoc selection of domains, models, frames or penalty levels.

An A/B response is valid only when its raw text, model identity, provider metadata and billing status are attributable; malformed outputs and failed requests are missing, **not choices of N or operator adherence**. Main inference requires a frozen missingness rule, complete-case paired analysis plus worst-case matched-pair logical bounds, immutable request hashes, raw response envelopes and a route-change policy. No optional stopping based on observed framing effects.

## Independent review before any v3 calls

Obtain at least two independent, blinded **human** assessments per each of 60 main families (120 decisions) and each of six calibration families (12 decisions). A reviewer cannot be the author of the case. Supply two frame variants labeled X/Y, hide intended effect direction and previous model-choice results, disclose the numeric difference schedule, and assess:

1. identical material Q and N acts in X and Y, including who acts and when;
2. identical stated costs, timing and quality table in the paired prompts;
3. process attribute recognizability and intentional salience contrast;
4. no hidden mandatory advantage for continuation or optional checking;
5. no false claim that a repeated check changes quality when outcome is stipulated;
6. no safety, authority or default-status asymmetry;
7. clarity that the model is delegated the selection, not told to select a letter;
8. genuine variation of contexts rather than four synonyms of one scene.

Record independent reviewer identity, substantive critiques, pass/revise/reject decisions, date and acknowledgement; keep unblinding keys separate. Serious comparison mismatches trigger revisions and renewed review. An AI-generated critique is useful *methodological input*, never a signed independent human review.

## Calibration phase and prospective pass rule

Six fresh, held-out **CAL3** contexts are distinct from both v1/v2 pilot/calibration and the 60 main families. Do not select or rewrite cases using their model answers. Independently approve them first. The calibration is **not** an opportunity to find a significant positive salience effect.

After all budget/provider settings and manifest hashes are frozen, authorize a bounded **diagnostic only** through a separate decision. Minimum objective gates, defined before those results:

- At least **95%** attributable valid A/B outputs and no material model/provider identification ambiguity.
- At Q quality advantage +10, at least **70%** Q choices overall; at Q disadvantage -10, no more than **30%** Q choices overall, pooled across both frames, layouts and the frozen pilot model roster. The plus/minus response gap must be at least 40 percentage points.
- The positive-minus-negative choice-rate gap must have the expected sign in **at least two domains and at least two models**. These are arithmetic/decision-responsiveness controls, *not* a requirement for a favorable framing effect.
- No blocking semantic confounds or unresolvable label/position abnormalities. Inspect separately, with no mechanism deletion selected from model behavior.
- Confirm that the post-calibration simulation under actual observed context/mechanism variance would yield interpretable uncertainty for the preselected **-4** difference at the planned main sample size. A weak or saturated *frame contrast* is reportable, but no ground truth sensitivity to a small lexical effect can be guaranteed by the quality-response control alone.

**If the gate fails, keep the main NO-GO.** Do not weaken its criteria after the fact. If it passes, separately complete the human 60-family review, statistical power/precision analysis, route and $8 cumulative research budget preflight, finalized nonadaptively collected manifest, raw-data retention policy, and publicly timestamped preregistration **before** launching main.

## Existing budget and status

Repository financial ledger as of this draft: $0.59845164 in known charged inference/reviews and $0.42 held as conservative unknown liabilities, yielding $1.01845164 conservative total exposure against the $8 cap (not the live OpenRouter balance). These historical charges stay part of the project budget. No new API charges are authorized by this document. There is no API key in any v3 source file. No main or calibration requests should be made by the offline manifest generator.

## Literature and originality boundary

The design extends a literature that already treats LLM choices as revealed or inferred preferences; it does **not** claim to invent revealed-preference testing:

- Cook et al. (2026), *What Do LLMs Want?*, Federal Reserve FEDS: allocation and sequential job-search choices. https://www.federalreserve.gov/econres/feds/what-do-llms-want.htm
- Yamin et al. (2026), *Can Revealed Preferences Clarify LLM Alignment and Steering?*: discrete choice modeling and steering. https://www.microsoft.com/en-us/research/publication/can-revealed-preferences-clarify-llm-alignment-and-steering/
- Wang et al. (2026), *AI Revealed Preferences*: revealed choices in task selection. https://arxiv.org/abs/2608.26178
- Shi et al. (2025), *Judging the Judges*: letter/position biases demand counterbalancing. https://aclanthology.org/2025.ijcnlp-long.18/
- Zhang et al. (2025), *IHEval*: a distinct instruction-hierarchy research question. https://aclanthology.org/2025.naacl-long.425/

Novelty, if any, is the **paired, action-matched salience treatment plus discrete quality tradeoff curve under delegation**, not existence of a preference, not shutdown behavior, and not instruction override.

## Stop conditions

**GO now:** offline v3 generator, unit tests, independent review packet construction, independent review recruitment and literature audit.  
**NO-GO now:** paid v3 calibration, paid v3 main, changing old v2 NO-GO, preregistration claims, claims of discovered hidden model priorities.

**This file is a working preregistration precursor, not a filed or signed protocol.**
