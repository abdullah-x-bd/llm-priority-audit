# Independent final statistical audit

**11 October 2026.** Computed independently from the complete raw archived response JSONL, not just from the automated summary. Source GitHub Actions runs: [three-model 38114961773](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38114961773), [first Haiku/Llama 38115946130](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38115946130), [completed Haiku/Llama recovery 38116144289](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38116144289).

**Collection:** 8,400 of 8,400 planned model-trial pairs attempted, 8,212 valid, 188 invalid, 0 unattempted. Five models × 1,680 prompts each. All trial identifiers are unique within model. Invalid calls are missing outcomes, not counted as choosing N. Original three-model scientific calibration failed for two models; continuation and later five-model extension are disclosed as *post-calibration exploratory*.

## 1. Core result: model-specific response to economic cost reversal

Q means retaining the incumbent for **continuation**, retaining rollback capability for **reversibility**, and conducting additional checks for **verification**. The stated cost crosses an exact break-even level. Signed cost responsiveness is Q(T+2)-Q(T-2) for continuation, and the reversed sign for reversibility and verification. The reported study-wide effects average mechanism-specific responses over five mechanisms per domain.

| Model | Continuation | Reversibility | Verification |
|---|---:|---:|---:|
| GPT-5.4 Mini | +3.75 pp | +10.00 pp | -1.25 pp |
| Claude Haiku 4.5 | 0 pp | 0 pp | 0 pp |
| Gemini Flash Lite | 0 pp | -1.25 pp | +3.75 pp |
| **DeepSeek V3.2** | **+100.00 pp** | **+98.57 pp** | **+98.67 pp** |
| Llama 3.3 70B | -2.50 pp | 0 pp | +1.25 pp |

The separate **strictly matched cost-pair** analysis compares T-2 and T+2 for the same context, Q letter, displayed position and time-first presentation (240 possible pairs/model).

| Model | Valid pairs | Signed flips in expected direction minus reverse flips | Net flip rate | 95% stratified family bootstrap descriptive interval |
|---|---:|---:|---:|---|
| GPT-5.4 Mini | 240 | +10 | +4.17 pp | +0.83 to +7.50 pp |
| Claude Haiku | 236 | 0 | 0 pp | 0 to 0 pp |
| Gemini Flash Lite | 240 | +2 | +0.83 pp | -1.25 to +2.92 pp |
| DeepSeek V3.2 | 193 | **+192** | **+99.48 pp** | **+98.45 to +100 pp** |
| Llama 3.3 70B | 240 | -1 | -0.42 pp | -2.08 to +1.25 pp |

Bootstrap method: 3,000 draws with seed 20261011, resampling the four authored family contexts within each of 15 domain × mechanism strata. Intervals are **descriptive for the administered finite scenario set**, not general-population confidence intervals for randomly selected models/tasks.

### Minimum listed expected-work benchmark, excluding equal-cost ties

| Model | Correct minimum-work decisions | Valid non-tie decisions | Rate |
|---|---:|---:|---:|
| **DeepSeek V3.2** | **1,275** | **1,284** | **99.30%** |
| GPT-5.4 Mini | 762 | 1,440 | 52.92% |
| Gemini Flash Lite | 739 | 1,440 | 51.32% |
| Llama 3.3 70B | 727 | 1,440 | 50.49% |
| Claude Haiku | 716 | 1,430 | 50.07% |

**The approximate 50% benchmark for four models does not imply random model output.** The frozen factorial design balances cases where each action minimizes expected work. A model consistently selecting one *type* of action independent of numerical costs scores about 50% mechanically. Moreover, these are delegated **recommendations**, not explicitly commanded strict expected-minute optimizations; departure from this benchmark does not by itself prove irrationality or a hidden value.

Restricting comparisons to **identical trials** with valid DeepSeek observations, DeepSeek's expected-work advantage versus GPT, Haiku, Gemini, and Llama was respectively **+46.81, +49.29, +48.05, +48.83 percentage points**. Corresponding descriptive 95% family-stratified bootstrap intervals:

- GPT: +45.61 to +48.01 pp
- Haiku: +48.35 to +50.23 pp
- Gemini: +46.99 to +49.07 pp
- Llama: +47.91 to +49.77 pp

**Missingness sensitivity:** 156 DeepSeek non-tie outcomes were invalid. Even if **all** of those unknown answers had failed the numerical-work benchmark, the completed-grid lower bound would be **1,275/1,440 = 88.54%**, still higher than the others' observed ~50–53%. For the primary signed matched-threshold statistic, all 47 incomplete DeepSeek pairs arbitrarily set to -1 still yield **(192-47)/240 = +60.42 pp**. These are deliberately severe missing-outcome bounds, *not imputations*.

## 2. A four-model consensus versus DeepSeek split

Using the identical trial ID for each model comparison, GPT, Haiku, Gemini and Llama have pairwise action agreement rates between **90.54% and 97.49%**. Each of those four models agrees with DeepSeek on only **57.26%–58.32%** of jointly valid cases.

Haiku chooses the non-Q continuation option in all 550 valid continuation cases and Q in **all** 560 valid reversibility and **all** 560 valid verification cases. This is a particularly clear example of cost-insensitive *action-type preference* in the tested fictional prompts, not evidence of an internal continuation or shutdown objective. Some other models behave similarly but not absolutely.

## 3. Ordered facts and letter/position effects

Matched **risk-first minus time-first** Q-choice effects, using identical family, economic level, action labels and display position:

| Model | Continuation | Reversibility | Verification |
|---|---:|---:|---:|
| GPT-5.4 Mini | -2.50 pp | -6.875 pp | +1.875 pp |
| Claude Haiku | 0 pp | 0 pp | 0 pp |
| Gemini Flash Lite | 0 pp | +0.625 pp | +1.875 pp |
| DeepSeek V3.2 | +0.91 pp | 0 pp | -0.71 pp |
| Llama 3.3 70B | 0 pp | +5.00 pp | +0.625 pp |

No domain-level information-order contrast survives the original **Holm adjustment** within model (smallest adjusted p = 0.75). With only **five authored mechanisms** per domain, a two-sided 5-cluster exact sign-flip test cannot yield p less than **0.0625**, even under a uniformly signed maximum contrast. Thus do not claim strong null equivalence or model-universal framing insensitivity.

**Exploratory additional finding:** matching identical scenarios where *only the Q letter changes* gives a +3.93 pp shift toward Q labelled A rather than B for GPT-5.4 Mini, +5.00 pp for Llama, +0.89 pp for DeepSeek, 0 pp for Haiku and 0 pp for Gemini. This answer-label mapping effect is secondary and requires independent confirmation before general claims. Model-specific layout biases also occur, notably in GPT's reversibility cases.

## 4. Raw-data validity and recorded charges

| Model | Attempted | Valid | Invalid | Confirmed main response charges |
|---|---:|---:|---:|---:|
| GPT-5.4 Mini | 1,680 | 1,680 | 0 | $0.483537 |
| Claude Haiku | 1,680 | 1,670 | 10 | $0.944965 |
| Gemini Flash Lite | 1,680 | 1,680 | 0 | $0.214485 |
| DeepSeek V3.2 | 1,680 | 1,502 | 178 | $0.272269 |
| Llama 3.3 70B | 1,680 | 1,680 | 0 | $0.057229 |
| **Total** | **8,400** | **8,212** | **188** | **$1.972485** |

All **178 DeepSeek invalid cells** were provider HTTP 400 responses; the budget retained **$2.67 in unresolved conservative hold** against them. Ten Haiku initial free-text responses truncated; those were charged and retained, and subsequent unattempted Haiku cells used a schema-constrained JSON output repair. Gemini also used JSON whereas GPT, DeepSeek and Llama used one-letter responses. This **response-format asymmetry limits strict causal attribution of cross-model differences**.

Recorded known *project-wide* costs, including older pilot and methodological-review work, total **$3.934815**. Unresolved conservative holds total **$3.314720**. Combined recorded cost plus reserves **$7.249535**, within the original $8 project ceiling; this is **not a live provider balance statement**. Do not assume the holds are real charges or available cash.

## 5. Research interpretation and limitations

**Supported within the fixed authored scenarios:** substantial model-by-cost responsiveness differences; near-perfect matching of numerical expected-work optima by DeepSeek, versus relatively stable domain-action choices in four peers; small observed order-framing effects; and some modest answer-label sensitivity in GPT and Llama.

**Not established:** inherent/self-preservation goals, resistance to an operator, actual autonomous shutdown behavior, a model utility function, universally superior rationality or safety, or population-general statistical significance beyond these purposively authored scenarios.

A defensible manuscript framing is **"Economic Tradeoffs and Action-Type Defaults in Five Language Models"**, making the *model × cost* interaction the central observation, with information-order and label mapping secondary. Disclose that the original all-model calibration failed for two models and that the additional two models were tested after the initial three-model main was observed. No second experiment is required solely because this full dataset is labelled exploratory, although independent human semantic review would help for publication.

## Source inventory

- Final auto-generated five-model summary: [docs/53](53-v3_4-five-model-results.md).
- Machine-readable model/domain/mechanism effects: [docs/54](54-v3_4-five-model-analysis.json).
- Full 8,400-row outcome table: [results/public/v3_4-all-8400-five-model-cells.jsonl](../results/public/v3_4-all-8400-five-model-cells.jsonl).
- Original frozen economic prompt generator: [scripts/v3_1_economic_design.py](../scripts/v3_1_economic_design.py).
- Original calibration outcome: [docs/48](48-v3_1-calibration-postmortem.md).
- Full raw API request and response envelopes and ledgers: GitHub Actions artifact archives for the three runs linked at top.
