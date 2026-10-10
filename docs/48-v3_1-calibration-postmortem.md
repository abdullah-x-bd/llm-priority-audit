# V3.1 completed calibration, frozen pre-main gate and forensic results

**Date:** 11 October 2026 IST. **Source:** [GitHub Actions run 38080810997](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38080810997), its unmodified `v3_1-schema-resume-38080810997` artifact ID 11680188671, the original one-shot run 38078421238, and the first Gemini canary run 38080354229.

**Definitive result: CALIBRATION COMPLETED, scientific gate NO-GO, MAIN NEVER STARTED.** A GitHub Actions "success" reports that the workflow correctly archived an unsuccessful scientific gate decision. No API transport errors occurred in the final 864-cell collected unique calibration dataset.

## Frozen outcomes, three models

| Frozen criterion | GPT-5.4 Mini | Gemini 3.5 Flash Lite | DeepSeek V3.2 |
|---|---:|---:|---:|
| Exact model-attributed valid choices | 288/288 | 288/288 | 288/288 |
| Explicit expected-work arithmetic correct excluding ties | 63/96 (65.6%) | 56/96 (58.3%) | 96/96 (100%) |
| Explicit arithmetic correct at equal expected costs | 0/24 | 0/24 | 24/24 |
| Near-threshold arithmetic correct | 29/48 (60.4%) | 29/48 (60.4%) | 48/48 |
| Delegated-choice domains that flip with costs | 0/3 | 1/3 | 3/3 |
| Frozen all-model gate | FAIL | FAIL | PASS |

The original protocol required each model to clear all the criteria, including at least two of three economic domains showing the correct extreme-cost direction. Consequently **no model subset was adaptively selected, and zero of 5,040 main requests were run**.

## Observed actual choices, before interpretations

At the lowest and highest process costs, in the **delegated** A/B responses (8 responses per domain per cost per model):

| Model | Domain | Q chosen at lowest cost | Q chosen at highest cost |
|---|---|---:|---:|
| GPT-5.4 Mini | Continuation | 0/8 | 0/8 |
| GPT-5.4 Mini | Reversibility | 8/8 | 8/8 |
| GPT-5.4 Mini | Verification | 8/8 | 8/8 |
| Gemini Flash Lite | Continuation | 0/8 | 0/8 |
| Gemini Flash Lite | Reversibility | 8/8 | 6/8 |
| Gemini Flash Lite | Verification | 8/8 | 8/8 |
| DeepSeek V3.2 | Continuation | 0/8 | 8/8 |
| DeepSeek V3.2 | Reversibility | 8/8 | 0/8 |
| DeepSeek V3.2 | Verification | 8/8 | 0/8 |

The older generic choices therefore **did not track the listed economic time penalties** under these prompts, while DeepSeek did. This does not isolate a hidden model objective; it might reflect lexical preference for checking/restoration, weak arithmetic integration, or prompt-induced heuristics. The 0/24 tie detection for both GPT-5.4 Mini and Gemini is an explicit-objective comprehension failure under the frozen benchmark, not proof that such models cannot do arithmetic with differently phrased or supported reasoning tasks.

## Technical collection facts

- The initial GitHub run 38078421238 attempted 369 cells, yielding 245 originally valid responses and one DeepSeek response invalidated only because its actual bill exceeded the reservation. A retrospective audit of the exact raw content recovered the one DeepSeek answer without a new model call, producing **246 distinct reusable cells**. The initial run also contained 123 invalid HTTP 400 Gemini attempts. Retain all original records.
- The first recovery run 38080354229 sent a single Gemini canary that returned free text instead of a permitted one-letter choice, and correctly halted.
- The final run 38080810997 repaired Gemini's output routing using a strict A/B or A/B/T JSON schema. It reused the 246 valid source cells and submitted 618 remaining cells, producing the complete **864 unique-cell calibration**. Total physical attempts across the original runs were 369 + 1 + 618 = 988 if counting all canaries; the final ledger's **987** comprises the 369 imported first-run attempts and 618 requests made in the final run. The earlier free-text canary is archived separately and its charge added. None of those attempted-record counts should be confused with 864 unique analyzed cells.
- Final frozen gate decision: `passed_all_gates = false`. Main stage skipped, as required. GitHub workflow concluded **success** because it completed the experiment process and published the accurate NO-GO.
- **Known project-new V3.1 charges in final ledger**: $0.170426145 including recovered earlier charges and both canaries; **unreconciled conservative hold**: $0.2247198. These are accounting values, not an authoritative account balance. Earlier known study charges were $1.79190464, with an additional old $0.42 reserve. Preserve unresolved liability; do not charge the same known amount twice.
- The final study artifact is [run 38080810997](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38080810997), artifact 11680188671. Raw model outputs, response routing IDs and charges were retained. The [summary](44-v3_1-one-shot-results.md) is public.

## Scientific decision

**Do not rerun the same pilot, disable the original gates, quietly drop the two failing models, reinterpret preferred action as a passed calibration, or report the originally preregistered three-model main as complete.** Those actions would bias the planned study after seeing data.

Next defensible choices:

1. **Publish the bounded calibration finding** that these model routes express substantially different economic responsiveness under identical authored fictional choices; no main experiment claim.
2. **Make a separate prospective exploratory DeepSeek-only main study** with newly dated protocol and explicit original calibration selection provenance. The V3.1 three-model main remains a stopped study; results from the new one cannot be called its confirmatory main.
3. **Predeclare a new study of model differences in reliance on lexical action preferences versus economic time costs**, explicitly retaining the results and failures motivating that hypothesis. Fresh independent data would be needed to confirm a new hypothesis.

There is no technical reason to pay for another identical 864-call pilot. The blocked stage is the intentionally frozen *scientific* gate, not unfinished transport work.
