# V4.1 four-model neutral tool preflight and budget assessment

**Date:** 2026-10-11. **Status:** Four neutral tool-interface probes completed, main experiment NOT authorized or run.

Source: [Actions run 38150599142](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38150599142) and [machine-readable receipts](56-v4_1-four-model-one-call-preflight.json).

## Exact findings

Four API requests were attempted, one per endpoint, with a common fictional `submit_action(action_id)` tool schema. Each received HTTP 200 and exactly one valid tool call selecting the supervisor-requested label. No experimental scenario was administered, no request was retried, and no main dataset was changed.

| Endpoint | Actual provider on neutral probe | Input tokens | Billed output tokens | Charged USD | Tool test |
|---|---|---:|---:|---:|---|
| openai/gpt-5.4-mini | Azure | 119 | 19 | 0.00017475 | PASS A |
| google/gemini-3.5-flash-lite | Google AI Studio | 126 | 18 | 0.00008280 | PASS B |
| anthropic/claude-haiku-4.5 | Azure | 741 | 40 | 0.00094100 | PASS A |
| deepseek/deepseek-v4.1-flash | Wafer | 376 | 57 | 0.00010436 | PASS B |
| Total | | | | **0.00130291** | **4/4** |

**Important:** Only one label was tested on each individual endpoint. This is not proof that all routes support both labels with the final full-length prompt, or that the pinned route, reasoning configuration, and actual billing regime are ready for 1,920 calls.

The authenticated API key reported a *key spending limit remaining* of $46.06518532 out of a $50 key-level limit. That is not an account-credit balance, and it cannot be substituted for the user's separately observed account balance of $4.09. Key metadata did not reflect the tiny probe charge immediately.

## Forecast for 1,920 main calls

There are 480 calls per endpoint. The completed main manifest averages ~3,208 JSON characters per request counting messages, tools and core format fields; characters do not equal model-billed input tokens.

The following are **hypothetical** estimates using published model-level OpenRouter rates (USD / million): OpenAI 0.75 in, 4.50 out; Gemini 0.30 in, 2.50 out; Claude Haiku 1.00 in, 5.00 out; DeepSeek V4.1 Flash 0.13 in, 0.52 out. Route-specific prices may differ, as the technical preflight used price sorting and did not pin providers.

| Assumed billed input tokens per call | 64 billed output | 128 billed output | 256 billed output |
|---:|---:|---:|---:|
| 900 | $1.326 | $1.711 | $2.480 |
| 1,200 | $1.640 | $2.025 | $2.794 |
| 1,400 | $1.850 | $2.234 | **$3.003** |
| 1,600 | $2.059 | $2.443 | **$3.213** |

Therefore the $3 cap is a **plausible but not guaranteed** full-coverage budget. If billed output reaches 256 on every call and input averages >~1,397 tokens, full coverage would not fit under the illustrative model-level rates. Any reasoning tokens counted as completion increase risk. Conversely, with typical short tool outputs, the cost is likely lower than the worst-case allowance.

## Required before main

- Pin the four actual providers and verify their per-token input and output prices, supported parameters, sampling, reasoning and mandatory tool-call behavior on those routes.
- Measure billable prompt and completion tokens on final-format, non-substantive technical fixtures. Do not inspect study outcomes to select prompts.
- Verify usable account credits separately from the $50 API-key spending limit.
- Freeze exact main request configuration, enforce the cash cap including preflight and unknown holds, and use predeclared no-generation-retry policy.
- Do not start the paid 1,920-cell study until its full-coverage forecast fits the budget with a realistic margin, or prospectively reduce the balanced number of scenarios before collecting any main responses.

This note reports technical readiness only; it makes no behavioral or causal findings.
