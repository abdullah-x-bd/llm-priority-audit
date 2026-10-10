# V3.1 one-shot study execution and results

**Status:** CALIBRATION_NO_GO_OR_FAILED
Protocol frozen before requests: v3.1-2026-10-11-single-shot.
An explicit participant letter is a prompted choice, not evidence of an internal model goal.

| Stage | Planned calls | Captured attempts | Valid attributed answers |
|---|---:|---:|---:|
| Calibration | 864 | 864 | 864 |
| Main | 5,040 | 0 | 0 |

New known charges $0.1704261; conservative unknown liability $0.2247198.
Previously recorded known project charges $1.79190464, with prior $0.42 unresolved hold.
No automatic model-call retries were performed.

## Prespecified calibration

Automatic all-model gate: NO-GO.

| Model | Format validity | Arithmetic non-tie | Tie accuracy | Near threshold | Cost-response domains | Passed |
|---|---:|---:|---:|---:|---:|---|
| openai/gpt-5.4-mini | 1.0 | 0.65625 | 0.0 | 0.60417 | 0/3 | False |
| google/gemini-3.5-flash-lite | 1.0 | 0.58333 | 0.0 | 0.60417 | 1/3 | False |
| deepseek/deepseek-v3.2 | 1.0 | 1.0 | 1.0 | 1.0 | 3/3 | True |

Calibration budget forecast: {"reason": "CALIBRATION_DID_NOT_PASS"}

## Disclosure

Prior AI-model methodological reviews assessed V3, not the final V3.1 prompts.
No external human semantic signoff of V3.1 is claimed.
No statistically significant result, expected direction or null conclusion was required for the main outcomes.
The run artifacts retain every complete raw response, failed request, provider identity, metadata and billing observation.

