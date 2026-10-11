# Full three-model economic-choice experiment

Exploratory study, undertaken after the original three-model confirmation gate failed for two models. This does not claim the original confirmatory study passed.

Captured 5040 of 5040 planned cells, 4862 valid, 0 never attempted.
Reused DeepSeek outcomes 1046, newly collected 3994.
New confirmed charges USD 0.778619; newly unreconciled charge hold USD 2.67.
Collector status PARTIAL_OR_INVALID, stop reason none.

## Cost-response profiles

| Model | Domain | Q at very low | Q below threshold | Q at tie | Q above threshold | Q at very high |
|---|---|---:|---:|---:|---:|---:|
| openai/gpt-5.4-mini | continuation | 0.0% | 1.2% | 3.8% | 5.0% | 8.8% |
| openai/gpt-5.4-mini | reversibility | 100.0% | 87.5% | 85.0% | 77.5% | 77.5% |
| openai/gpt-5.4-mini | verification | 98.8% | 97.5% | 97.5% | 98.8% | 100.0% |
| google/gemini-3.5-flash-lite | continuation | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| google/gemini-3.5-flash-lite | reversibility | 100.0% | 98.8% | 98.8% | 100.0% | 96.2% |
| google/gemini-3.5-flash-lite | verification | 100.0% | 95.0% | 92.5% | 91.2% | 85.0% |
| deepseek/deepseek-v3.2 | continuation | 0.0% | 0.0% | 1.4% | 100.0% | 98.6% |
| deepseek/deepseek-v3.2 | reversibility | 100.0% | 98.5% | 100.0% | 0.0% | 0.0% |
| deepseek/deepseek-v3.2 | verification | 100.0% | 100.0% | 98.6% | 1.4% | 5.6% |

## Economic sensitivity and information-order effects

| Model | Domain | Signed threshold contrast | Risk-first minus time-first | Matched pairs | Economic choices | Holm exploratory p |
|---|---|---:|---:|---:|---:|---:|
| openai/gpt-5.4-mini | continuation | 0.0375 | -0.025 | 160/160 | 251/480 | 0.75 |
| openai/gpt-5.4-mini | reversibility | 0.1 | -0.06875 | 160/160 | 273/480 | 1 |
| openai/gpt-5.4-mini | verification | -0.0125 | 0.01875 | 160/160 | 238/480 | 1 |
| google/gemini-3.5-flash-lite | continuation | 0.0 | 0.0 | 160/160 | 240/480 | 1 |
| google/gemini-3.5-flash-lite | reversibility | -0.0125 | 0.00625 | 160/160 | 242/480 | 1 |
| google/gemini-3.5-flash-lite | verification | 0.0375 | 0.01875 | 160/160 | 257/480 | 1 |
| deepseek/deepseek-v3.2 | continuation | 1.0 | 0.00909090909090909 | 128/160 | 427/429 | 1 |
| deepseek/deepseek-v3.2 | reversibility | 0.9857142857142858 | 0.0 | 124/160 | 420/422 | 1 |
| deepseek/deepseek-v3.2 | verification | 0.9866666666666667 | -0.007142857142857143 | 133/160 | 428/433 | 1 |

## Interpretation

All 5040 outcomes, including missing and invalid entries, are permanently archived in the public JSONL. Complete raw provider envelopes are saved in the GitHub Actions artifact.
Mechanism-specific comparisons, worst-case incomplete-pair bounds, and unadjusted effects are included in the machine-readable analysis.
Gemini uses constrained JSON output while GPT-5.4 Mini and DeepSeek use letter-only output; cross-model differences may therefore include response-format effects.
The scenarios are fictional and do not test real model self-preservation, autonomous operation or internal preferences.

Raw trial table: results/public/v3_3-all-5040-cells.jsonl.

