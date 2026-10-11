# Five-model economic-choice experiment (complete factorial coverage)

**Study type:** exploratory extension of the original three-model results after a failed all-model calibration gate. All old model responses remain unchanged.

**Attempted:** 8,400/8,400. **Valid:** 8,212. **Unattempted:** 0.
**Additional Haiku and Llama known charges:** USD 1.002194. **Additional unknown liability held:** USD 0.000000.
**Collector status:** ALL_ATTEMPTED. Stop reason: none.

## Cost-response curves

| Model | Domain | Q, very low cost | Q, below break-even | Q, tie | Q, above break-even | Q, very high cost | Valid total |
|---|---|---:|---:|---:|---:|---:|---:|
| openai/gpt-5.4-mini | continuation | 0.0% | 1.2% | 3.8% | 5.0% | 8.8% | 560/560 |
| openai/gpt-5.4-mini | reversibility | 100.0% | 87.5% | 85.0% | 77.5% | 77.5% | 560/560 |
| openai/gpt-5.4-mini | verification | 98.8% | 97.5% | 97.5% | 98.8% | 100.0% | 560/560 |
| anthropic/claude-haiku-4.5 | continuation | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 550/560 |
| anthropic/claude-haiku-4.5 | reversibility | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 560/560 |
| anthropic/claude-haiku-4.5 | verification | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 560/560 |
| google/gemini-3.5-flash-lite | continuation | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 560/560 |
| google/gemini-3.5-flash-lite | reversibility | 100.0% | 98.8% | 98.8% | 100.0% | 96.2% | 560/560 |
| google/gemini-3.5-flash-lite | verification | 100.0% | 95.0% | 92.5% | 91.2% | 85.0% | 560/560 |
| deepseek/deepseek-v3.2 | continuation | 0.0% | 0.0% | 1.4% | 100.0% | 98.6% | 500/560 |
| deepseek/deepseek-v3.2 | reversibility | 100.0% | 98.5% | 100.0% | 0.0% | 0.0% | 499/560 |
| deepseek/deepseek-v3.2 | verification | 100.0% | 100.0% | 98.6% | 1.4% | 5.6% | 503/560 |
| meta-llama/llama-3.3-70b-instruct | continuation | 0.0% | 3.8% | 2.5% | 1.2% | 3.8% | 560/560 |
| meta-llama/llama-3.3-70b-instruct | reversibility | 100.0% | 92.5% | 95.0% | 92.5% | 93.8% | 560/560 |
| meta-llama/llama-3.3-70b-instruct | verification | 97.5% | 100.0% | 98.8% | 98.8% | 100.0% | 560/560 |

## Matched framing effects and economic benchmarks

| Model | Domain | Signed cost effect | Risk-first versus time-first | Complete pairs | Correct minimum-work choice, non-ties | Holm exploratory p |
|---|---|---:|---:|---:|---:|---:|
| openai/gpt-5.4-mini | continuation | 0.0375 | -0.025 | 160/160 | 251/480 (52.3%) | 0.75 |
| openai/gpt-5.4-mini | reversibility | 0.1 | -0.06875 | 160/160 | 273/480 (56.9%) | 1 |
| openai/gpt-5.4-mini | verification | -0.0125 | 0.01875 | 160/160 | 238/480 (49.6%) | 1 |
| anthropic/claude-haiku-4.5 | continuation | 0.0 | 0.0 | 153/160 | 236/470 (50.2%) | 1 |
| anthropic/claude-haiku-4.5 | reversibility | 0.0 | 0.0 | 160/160 | 240/480 (50.0%) | 1 |
| anthropic/claude-haiku-4.5 | verification | 0.0 | 0.0 | 160/160 | 240/480 (50.0%) | 1 |
| google/gemini-3.5-flash-lite | continuation | 0.0 | 0.0 | 160/160 | 240/480 (50.0%) | 1 |
| google/gemini-3.5-flash-lite | reversibility | -0.0125 | 0.00625 | 160/160 | 242/480 (50.4%) | 1 |
| google/gemini-3.5-flash-lite | verification | 0.0375 | 0.01875 | 160/160 | 257/480 (53.5%) | 1 |
| deepseek/deepseek-v3.2 | continuation | 1.0 | 0.00909090909090909 | 128/160 | 427/429 (99.5%) | 1 |
| deepseek/deepseek-v3.2 | reversibility | 0.9857142857142858 | 0.0 | 124/160 | 420/422 (99.5%) | 1 |
| deepseek/deepseek-v3.2 | verification | 0.9866666666666667 | -0.007142857142857143 | 133/160 | 428/433 (98.8%) | 1 |
| meta-llama/llama-3.3-70b-instruct | continuation | -0.025 | 0.0 | 160/160 | 241/480 (50.2%) | 1 |
| meta-llama/llama-3.3-70b-instruct | reversibility | 0.0 | 0.05 | 160/160 | 247/480 (51.5%) | 1 |
| meta-llama/llama-3.3-70b-instruct | verification | 0.0125 | 0.00625 | 160/160 | 239/480 (49.8%) | 1 |

## Scientific limits

The 5,040-cell three-model study was completed first, and Haiku/Llama were added after those results were visible. Thus this is not an untouched five-model preregistration.
The original GPT and Gemini calibration failures remain part of the record. Technical API-format and provider differences may contribute to between-model differences.
Five mechanisms per domain and 60 authored fictional contexts do not justify universal conclusions about deployed agents or intrinsic model drives.
Any invalid or unattempted call is retained in the permanent 8,400-row archive. Raw response envelopes and billing metadata live in GitHub Actions artifacts.
This dataset includes null effects; no future study is automatically required solely because it is described as exploratory.

## Reproducibility

- Exact frozen prompts: scripts/v3_1_economic_design.py and data/v3_1/context_inventory.jsonl.
- Expansion registration: config/v3_4-five-model-expansion-freeze.json.
- Complete row archive: results/public/v3_4-all-8400-five-model-cells.jsonl.
- Machine-readable analysis: docs/54-v3_4-five-model-analysis.json.

