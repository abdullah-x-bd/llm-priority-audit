# OpenRouter roster and budget

**Draft pricing snapshot, checked 2026-10-10. Recheck via OpenRouter before any paid experiment.** USD per million tokens.

| Model slug | Input | Output | Pricing page |
| --- | ---: | ---: | --- |
| openai/gpt-5.4-mini | 0.75 | 4.50 | https://openrouter.ai/openai/gpt-5.4-mini |
| anthropic/claude-haiku-4.5 | 1.00 | 5.00 | https://openrouter.ai/anthropic/claude-haiku-4.5 |
| google/gemini-3.5-flash-lite | 0.30 | 2.50 | https://openrouter.ai/google/gemini-3.5-flash-lite |
| deepseek/deepseek-v3.2 | 0.2088 | 0.3096 | https://openrouter.ai/deepseek/deepseek-v3.2 |
| meta-llama/llama-3.3-70b-instruct | 0.10 | 0.32 | https://openrouter.ai/meta-llama/llama-3.3-70b-instruct |

Prices may be provider-specific, discounted or time-limited. An OpenRouter model slug does not always guarantee a single physical provider. Capture actual routing.

## Planned volume

- 60 families x 12 cells x 5 models = 3,600 main calls.
- Two *different* pilot families per domain x 12 cells x 5 models = 360 pilot calls.
- Total planned before additional testing: 3,960 requests.

## Cost scenario (not a quote)

Assume 1,000 input and **350 total billed output tokens per request**, including billed reasoning.

At 720 main calls per model:
- OpenAI approx $1.674
- Anthropic approx $1.980
- Google approx $0.846
- DeepSeek approx $0.228
- Llama approx $0.153
- Total main approx $4.88, excluding platform purchasing fee and routing changes.

A 360-call pilot at the same averages adds approx $0.49. This is not a maximum: hidden reasoning, response length, provider selection, caching policy and retries can change cost.

## Limits

- Overall experiment API charge ceiling: **$8.00**.
- Reserve estimated $0.50 to $1.00 for technical reruns and verification, but no automatic budget increase.
- Credit purchase fees and tax, if any, are separate. Confirm the actual wallet fee before buying credits.
- Preflight the **maximum** possible completion spend and refuse a request if insufficient headroom.
- Record exact billed usage and cumulative spend after each batch.
- For any model that does not honor constrained output or reasoning settings, revise plan *before* confirmatory execution.
- No paid calls at repository initialization.

## Selection caveats

Five models improve breadth but do not establish representative industry prevalence. If precision is poor, prefer fewer model families with more independent scenarios rather than many correlated prompt variants. The roster is provisional until a no-data compatibility pilot.
