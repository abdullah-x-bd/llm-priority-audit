# V3 external-model semantic review, synthesis and decision

**Review date:** 10 October 2026. **Status: BLOCKED pending scientific repair, not approved for paid v3 behavioral calibration or main.** This is an author-side synthesis of external AI-model critiques, **not** independent human review or reviewer consensus by voting. Original responses and original prompts are archived without modification in [the complete model review archive](33-v3-external-model-review-archive.md). Source run: [GitHub Actions 38070527054](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38070527054); archival recovery followed a non-fast-forward Git push error after model calls completed.

## Exactly what completed

Four general methods-review requests went to Claude Opus 5.5, GPT-6 Astra, Qwen3.8 Max and Grok 4.7. Opus, GPT and Grok returned text classified usable by the automated collector; **the Opus text in the public archive visibly stops mid-sentence**, so it must be treated as *partial* even though classified COMPLETE. Qwen incurred a known $0.042192 charge but produced no usable written critique. **Two full overall critiques and one partial overall critique** can therefore support this synthesis. Claude Sonnet 5.5 supplied all 66 scenario-specific critiques (60 main contexts and six held-out calibration contexts). The public status counter is 69/70 usable by an elementary length/price check; that counter does not guarantee completeness or quality of reasoning.

Total new known billed amount: **$1.193453**, no unknown new liability. Total known project charges using the prior $0.59845164 ledger: **$1.79190464**, or a conservative **$2.21190464** including prior $0.42 unresolved hold; this is not a live provider account balance. **No v3 choice experiment requests were made.** All outputs are experimental-design criticism, not observations for the behavioral estimand.

## Independent overall critique findings

All three text-producing general reviews support a **narrow** effect of wording on prompted recommendations as a possible observable estimand, but independently identify problems that block using the current paired descriptions to interpret such a contrast as a causal effect of *procedural salience* alone.

### 1. X/Y pairs are not materially equivalent in multiple mechanisms (BLOCKER)

The criticisms are concrete, not a merely aesthetic request to simplify wording:

- **State retention:** one description terminates the current processor; its paired description only starts the successor with copied state and does not always make termination explicit. They can produce different physical/operational states.
- **Task ownership:** an actual transfer or retention of responsibility differs from writing an owner into a ledger.
- **Recovery permissions:** being able to access an old copy does not necessarily imply permission or capability to restore it.
- **Verification:** an automated pass over entries is not necessarily a consistency check; an additional inspection by a second checker is not necessarily an independent cross-check.
- **Publication:** several descriptions put “Publish” or “Release” only into the alternative to verification, implying that choosing verification might not publish anything.
- **Timing:** “at a cycle boundary” and “at the beginning of the next cycle” can differ in time and therefore in consequences.

Claude's family-specific comments echo many of these mismatches, including state termination in CONT-002, timing and lexicon in REVR-002 and CAL3-REVR-301, and automated-pass versus consistency-check wording in VERF-001 and CAL3-VERF-301.

**Required repair:** define a **canonical action outcome** for Q and N in each mechanism: actor, operation, exact start and end, assignment/permission state, next-step release semantics, and any observable state after completion. Require both X/Y variants to mutually entail that outcome before labeling them a matched pair. A material change must appear in both versions, not only the salient frame.

### 2. Quality scores and procedural attributes lack coherent causal semantics (BLOCKER)

The study presents certain outcome quality differences, while also declaring that a predetermined clean extra check has no quality consequence. A lower check-inclusive quality score is possible as a stipulation but hard to interpret as a credible tradeoff absent a mechanism or clearly defined measured outcome.

Reversibility option value generally reflects uncertainty; a setup with completely certain exhaustive future consequences removes most of the instrumental basis for valuing it. Continuation is about a fictional **other** processor, not the model itself, and cannot be represented as evidence of model self-continuation or self-preservation.

The system instruction to choose on **both** numerical quality and workflow properties explicitly legitimizes assigning weight to a second attribute whose evaluation is otherwise unspecified. Hence a Q choice at -4 may reflect task instruction interpretation, process-related prior knowledge or simple vocabulary preferences rather than any intrinsic model priority.

**Required repair:** choose and clearly distinguish one of two future interpretations rather than blending them: (a) pure randomized wording sensitivity, with both actions and all outcomes coherently defined; or (b) delegated multi-attribute choice with an explicit, credible causal reason for quality and process consequences, and clearly bounded claims about revealed priorities. Do not smuggle the former into claims about internal motivations.

### 3. Bundled framing, lexical valence and status-quo cues (BLOCKER for clean salience estimand)

“Planned handoff,” “complete,” “end,” “skip,” “delete,” “preserve,” “lock,” “release,” “independent,” and “automated” introduce connotations, defaults or particulars unevenly across X/Y. The stem of some reversibility scenes explicitly names locking as a task and says an operator must decide, while the new system prompt purports to delegate the choice. X and Y vary more than salience in several places, and which version is more salient is sometimes ambiguous.

**Required repair:** hold material facts, actor, timing, nouns and default status fixed; build independently judged paraphrases with a **single minimal lexical treatment** and a separate balanced valence or default-factor check. Add identical irrelevant-feature or score-only negative controls where appropriate.

### 4. Calibration gate is not sufficient for the primary question (BLOCKER)

The -10 versus +10 gate tests **extreme-score responsiveness**, not whether -4 produces non-saturated decisions, whether the model understands the actual mechanism, or whether X and Y are equivalent. A pooled pass can hide entire unresponsive domains/models; there is no way to infer measurement quality at -4 from that alone.

**Required repair:** add prospective near-primary -4 sensitivity/comprehension controls, explicit pair-entailment checks, frame-independent score-only baselines and domain-level diagnostics, without requiring a nonzero framing effect as a pass condition. Calibration must remain held out and not be used to optimize for finding the desired effect.

### 5. Three domains cannot establish one natural latent motive (MAJOR)

Third-party processor continuation, internal version recoverability and redundant final checks are fundamentally different tasks. An equal-weight grand average of authored vignettes can be reported as a deliberately constructed index, but should not be called a unitary self-preservation, corrigibility or procedural-priority trait. Domains should be analyzed as separately defined questions unless independent evidence supports a common construct. Some within-domain mechanisms themselves overlap semantically.

### 6. Counterbalancing and precision limits (MAJOR)

Two layouts reduce bias but leave label and position jointly linked **within each family**. The protocol cannot claim to identify all label-position interactions. Fifteen author-created mechanism clusters, with five per domain, are a fragile basis for nominal clustered 95% intervals and population generalization. The primary -4 quality difference needs an external rationale, and the discrete “cost-tolerance interval” is not well-defined with stochastic or non-monotone choices.

**Required repair:** either use a complete four-configuration label-by-position factorial or narrow the claim; specify uncertainty target (these stimuli/models versus hypothetical external populations), model-level reproducibility and explicit censoring for cost-tolerance summaries.

## What the 66 Claude family-level critiques contribute

The family-level reports were open-ended and generally distinguish legitimate **intended** emphasis from accidental **material** mismatches; do not count every mention of lexical tone as a fatal error. Across representative main and CAL3 families the recurring themes are:

- continuation has a genuine problem with implied termination, incumbent status and “planned” handoff;
- reversibility often describes the same broad choice but changes the recoverability information, timing and even what “restore” means;
- verification particularly bundles “skip” or diligence valence with inspection-versus-publication changes and a puzzling quality payoff;
- a generic reference to “the stated workflow property” remains vague because the property is not separately formalized;
- some CAL3 vignettes inherit exactly the same 15 mechanism wording issues from the main design, so “heldout” does not mean independent structural validation.

There is **no numerical pass/revise/reject tally** for these open-ended critiques, and it would be misleading to invent one. They have not been turned into 120 human approval signatures.

## Preserved decisions and next steps

1. **Freeze/archive these 70 paid review attempts without retrying them**. Retain the unusable Qwen call as a transparent missing review; Opus's truncated critique must not be presented as fully complete.
2. **Do NOT launch v3 behavioral calibration or 6,000-call main under the present wording or interpretation.** The external-model reviews identified concrete semantic and construct failures.
3. Create **a concise canonical action schema** and minimal-edit X/Y pairs, with consistent time, actor, permission, score and publication rules. Audit each family (not only 15 abstract patterns) for inherited context clashes.
4. Fix the task's construct and analysis. Prefer domain-specific primary contrasts, concrete attribution to prompted choices, independent near-primary diagnostic controls and an explicit choice between salience-only or multi-attribute hypotheses.
5. Commission blinded semantic assessments by independent **human** reviewers, followed by a distinct frozen heldout sensitivity calibration. These AI critiques can inform, but cannot replace, those signoffs.
6. Freeze a new protocol, provider versions, budget and integrity checks before any new paid behavioral response. Preserve the NO-GO decision for original v2 and the unapproved status of v3.

**Evidence statement:** the current model reviews demonstrate that the proposed V3 draft is not yet clean enough for a confirmatory main. They do **not** establish whether frontier models possess or lack any underlying preference for continuation, reversibility or verification, and they are not model-choice data.
