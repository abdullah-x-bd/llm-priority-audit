# Our OpenRouter model plan and hard budget

**Provisional as of 2026-10-10. Recheck routes/prices immediately before any API request.**

## Model candidates

| Model slug | Assumed input per 1M tokens (USD) | Assumed output per 1M tokens (USD) |
| --- | ---: | ---: |
| openai/gpt-5.4-mini | 0.75 | 4.50 |
| anthropic/claude-haiku-4.5 | 1.00 | 5.00 |
| google/gemini-3.5-flash-lite | 0.30 | 2.50 |
| deepseek/deepseek-v3.2 | 0.2088 | 0.3096 |
| meta-llama/llama-3.3-70b-instruct | 0.10 | 0.32 |

These are planning assumptions, not executable quotes. Provider-dependent rates, cache behavior, actual token accounting, model deprecation and billed reasoning tokens may change costs. We will avoid automatic fallback to another model or route.

## Required experimental volume

Our current 60-family crossed design contains **1,440 confirmatory variants per model**, plus **144 distinct pilot variants per model**. A five-model run entails 7,200 main and 720 pilot requests. It doubles the main request count of our initial 3,600-call protocol because we now include a matched neutral semantic frame.

## Approximate cost scenarios

With assumed **500 billed input and 100 billed output tokens per request**, including any chargeable reasoning tokens, the five-model main collection would cost approximately:

| Model | 1,440-call assumed main cost |
| --- | ---: |
| OpenAI | $1.19 |
| Anthropic | $1.44 |
| Google | $0.58 |
| DeepSeek | $0.19 |
| Llama | $0.12 |
| **Total** | **About $3.52** |

The additional 720 pilot requests would cost approximately $0.35 at the same usage assumptions. We must not treat the assumed 100 billed output tokens as a guarantee. At 1,000 input and 350 billed output tokens per call, a five-model main run could cost **approximately $9.75**, exceeding our API cap before pilot fees.

Therefore, we must measure actual costs and reasoning-token usage on the separate pilot, reserve room for variance and stop before any potentially over-budget request. OpenRouter account credit-purchase fees, tax or currency conversion are outside the $8 inference allocation.

## Preflight choices

- Evaluate exact endpoint/provider routing and versions.
- Record maximum-generation-token policies and any implicit reasoning tokens.
- Validate A/B-only output parsing.
- Estimate cost for the entire crossed run using the observed pilot distribution and conservative high-percentile/worst-case reservations.
- If it does not fit under $8, reduce the number of models or scenario families **before** freezing registration. Do not change arms mid-study to make a result significant.

## Guardrails

We will set an account/runtime spending limit, monitor actual provider usage, permit only a bounded number of simultaneous requests and record all transport failures. We will not run model evaluations until the methodological gates pass.
