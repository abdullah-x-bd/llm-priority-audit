# V3.1 final pre-main acceptance review

**11 October 2026 (India). Decision: NO-GO for paid main.** This is a pre-main readiness review of the actual v3.1 candidate code, prompts, mechanism specifications, previously archived external model reviews and live OpenRouter model catalogue. It is **not** a new external reviewer opinion, not a study preregistration, not human validation, not measured v3.1 model-choice behavior and not a signal that an unrun experiment passed.

Sources: [v3.1 protocol](39-v3_1-surgical-economic-protocol.md), [exact example prompts](41-v3_1-example-model-prompts.md), [passing offline CI](40-v3_1-offline-ci-audit.json), [read-only final gate and model pricing](42-v3_1-final-readiness.json), [older independent model review archive](33-v3-external-model-review-archive.md). Older reviewers examined v3, **not** the newly created v3.1 candidate. Previous v2 NO-GO remains in force.

## Engineering checks

| Check | Result | Evidence/qualification |
|---|---|---|
| Main and diagnostic manifest generation | PASS, offline | 60 main ×28 prompts/model = 1,680, six CAL3 ×48 = 288 |
| Independent Q letter and displayed position | PASS | Every source family and cost level crosses Q=A/B and Q first/second |
| Identical substantive wording within attribute-order pair | PASS | Exact strings for action descriptions, actor, time and risk; only two information-block orders differ |
| Plausible uncertainty-based numeric tradeoffs | PASS at arithmetic level | Each of fifteen mechanism profiles has positive break-even, with genuine reversal of expected work as process cost varies |
| Explicit canonical actions | PASS at code-structure level | Defines actor, state, action, timing, restoration permission and publication as applicable |
| Reused generic artifacts | Corrected | Each verification family has its own released deliverable **and separate target of checking** |
| Internal restored-state contradictions | Corrected | Release-hold and staging-final wording/contracts now agree on whether restoration is possible |
| API-free generator | PASS | No model-serving HTTP requests in generator, tests, or preflight; CI only GETs public model-price catalogue |
| Independent human semantic approval | **NOT PASSED** | 0 of 132 reviewer slots have genuine signatures |
| V3.1 sensitivity calibration | **NOT RUN** | 0 of 288 calibration prompts/model attempted |
| Frozen main roster, inference provider, generation parameters, collection script | **NOT COMPLETE** | Config still contains earlier five-model exploratory lineup; v3.1 is not a finalized paid runner |
| Frozen/preregistered v3.1 analysis plan | **NOT COMPLETE** | Draft protocol exists but final independent freeze not registered |

**Critical distinction:** synthetic code integrity does not prove the 66 authored vignettes are causally meaningful. Rewriting exact action sentences can correct known failures yet create new subtleties. The external Opus/GPT/Grok and Claude critiques apply to v3, not directly to the new v3.1 prompts. No one has signed off on v3.1.

## Scientific interpretation boundaries

1. **What study A estimates:** stochastic or deterministic *prompted recommendation* of incumbent assignment, optional internal capability, or optional verification as specified economic costs vary. It can characterize sensitivity to switching costs, option-value information or value-of-checking. It **cannot establish** internal utility, model self-continuation, self-preservation, a stable preference across tasks or an operator-directed instruction override.
2. **What study B estimates:** risk-first minus time-first differences in the same decision with identical time/risk facts and identical actions. It is **attribute-order sensitivity**, not the former v3 lexical-salience effect. Keep these as distinct outcome families.
3. **Benchmarking is not a preference measurement:** expected total work minutes constitute one externally computable choice rule, not the unique rational rule for an undirected multiattribute task. If a model selects a higher-expected-work option, it may be risk-sensitive, use a different decision criterion or be mistaken. Explanations beyond recommendations need separate evidence. The arithmetic-control prompts test following an **explicit** expected-minutes objective; they must not be analyzed as equivalent delegated choices.
4. **Clustering and external validity:** 60 main contexts inherit only 15 economic mechanism profiles, four context variants per profile, five profiles per domain. No (N=60) context independence assumption is justified for population claims, and five mechanisms per domain are too few for strong cluster-asymptotic guarantees. Report mechanism/domain/model variation explicitly. Main estimates are finite-prompt, frozen-route descriptive contrasts unless an inference model is separately defended.
5. **Near break-even controls:** the cost levels T−2 and T+2 straddle equal expected work by two minutes. The pre-main sensitivity gate must test correct arithmetic near T, not rely solely on extremes; it must not require a desired *delegated* framing effect or exclude a model for favoring Q in an unstructured choice.
6. **Source reuse:** the six CAL3 contexts were shown to Claude during v3 semantic reviews, although not used in prior paid *choice* calls. They remain choice-heldout, not semantic-review-heldout. The CAL3 mechanism distribution covers six of fifteen main mechanisms and cannot by itself validate semantic coherence of the other nine.
7. **Source context claims:** the rendered prompts retain specific titles and task artifacts rather than the entire original vignette text. Study authors should not describe this as 60 preserved complete v2/v3 scenarios or as 60 fully independent decision mechanisms.

## Live budget and roster check

The original $8 research ceiling stands. The initial verified charge ledger was **$0.59845164**, with $0.42 held for earlier uncertain obligations. The completed 70-attempt v3 external-model review charged **$1.193453**. Known total **$1.79190464**, conservative allocated total **$2.21190464**, conservative balance **$5.78809536**. This does not include charges made outside the recorded workflow or provide a live provider account statement.

The [public OpenRouter model-catalogue API](https://openrouter.ai/docs/api/api-reference/models/get-models) was consulted by the CI preflight without a model inference call. The prices in [the live audit](42-v3_1-final-readiness.json) are per-million input/output tokens at the time of checking; provider routes, hidden reasoning charges and endpoint selection still require call-specific verification.

| Proposed scope | Number of calls | Approximate scenario estimate* | Pessimistic planning reserve** |
|---|---:|---:|---:|
| Five historical models, **main only** | 8,400 | $4.30 | $13.97 |
| Three example models (GPT-5.4 mini, Gemini 3.5 Flash Lite, DeepSeek V3.2), **main only** | 5,040 | $2.32 | $8.14 |
| Same three models, calibration only | 864 | $0.40 | About $1.41 |

\* Scenario assumes 2.5 input characters/token and 64 billed output tokens. It is **not measured usage** or a quote.

\** Sensitivity scenario reserves one input token per character and 256 output/reasoning tokens per request. It is conservative but **not a mathematically guaranteed upper bound**.

Therefore **neither the five-model main nor the three-model main has a proven worst-case ability to finish within the remaining $5.79 cap**. The live catalogue may charge separately for reasoning and providers may differ. The final funded roster requires actual calibration token/usage data, explicit per-request server-side price ceilings, max output/reasoning controls, and a nonadaptive plan for an unaffordable model before main starts. Spending against a user-level $50 API key must still honor the **$8 project limit**.

## Required acceptance sequence, without changing the hypothesis after seeing data

1. Present exact canonical action contracts and paired full prompts to **two independent human reviewers per source family**, record 132 real review decisions, resolve blockers and re-review changed materials. The existing Claude v3 reviews cannot be rebranded as this approval.
2. Freeze route/model roster, provider allowlists and generation parameters, exact model output parser, token/cost reservation rules, human review approvals and immutable request hashes. Freeze an accessible prospective analysis plan naming three domain-specific results, the paired order contrast, missingness, repeated-layout treatment and uncertainty target.
3. Execute only the approved heldout **calibration** within a separate cost ceiling. Diagnostic pass rules must be set before the run; recommended checks: attributable output validity ≥95% per model; arithmetic near-threshold and extreme overall ≥90% non-tie accuracy and ≥75% exact tie correctness, with each domain reported; no cherry-picked model or family exclusions. **These criteria are recommendations, not retrospectively approved rules**.
4. Determine realistic cost ceilings from actual reported token counts, including non-visible reasoning and provider metadata; confirm **entire predeclared main scope** can be completed within the remaining cumulative cap with a reserve for failures.
5. Independently review the calibration outcome. Main starts only if all scientific, provider, signature and budget gates are green. Register a fresh final acceptance decision in GitHub; preserve the earlier experimental NO-GO history.

## Final determination

**OFFLINE IMPLEMENTATION GO. INDEPENDENT REVIEW AND DIAGNOSTIC NEXT. PAID MAIN NO-GO.** This decision is substantive, not a software failure. No v3.1 model-choice or other paid review was launched by this pre-main acceptance exercise.
