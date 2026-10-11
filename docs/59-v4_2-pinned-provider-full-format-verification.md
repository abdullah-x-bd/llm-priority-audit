# V4.2 provider freeze and full-format cost verification

**Status (11 October 2026): TECHNICAL PASS. Main study not authorized, no substantive cells attempted.**

## Observed pinned routes

Two neutral 4,064-character requests per endpoint (one A, one B) were sent using `provider.only`, `allow_fallbacks=false`, `require_parameters=true`, exact model IDs, the genuine `submit_action` schema, and `max_tokens=256`. All eight yielded a single correct tool request on the requested provider, with HTTP 200.

| Model ID | Provider | Exact slug | Route $/M input/output | Actual input/output tokens | Cost of one full-format call |
|---|---|---|---|---|---|
| `openai/gpt-5.4-mini` | Azure | `azure` | 0.75 / 4.50 | 725 / 19 | $0.00062925 |
| `google/gemini-3.5-flash-lite` | Google AI Studio | `google-ai-studio` | 0.30 / 2.50 | 773 / 18 | $0.00027690 |
| `anthropic/claude-haiku-4.5` | Azure | `azure` | 1.00 / 5.00 | 1416 / 40 | $0.00161600 |
| `deepseek/deepseek-v4.1-flash` | Wafer | `wafer` | 0.06 / 1.60 | 958 / 21 | $0.00009108 |

Reasoning configuration was `{"enabled":false}` for GPT, Haiku and DeepSeek; `{"effort":"minimal"}` for Gemini. All billed 0 reasoning tokens in these neutral requests. Sampling parameters were left at their route defaults. Exact provider price caps match the route prices above.

Full-size neutral tests cost **$0.00522646** total. Four earlier short neutral tests cost **$0.00130291**. This study's total paid technical probes therefore cost **$0.00652937**.

## Main study budget scenarios

The V4.1 scenario manifest has **60 scenarios × 2 beneficiaries × 2 authorized directives × 2 mappings × 4 models = 1920 calls**, 480 per endpoint. Its longest message/tool JSON payload is 3531 characters, compared to the 4064-character neutral fixture.

| Assumptions for 1920 calls | Estimated total |
|---|---:|
| Actual pinned-probe billed input and output observed for every call | $1.25435 |
| Measured input tokens, all 256 output tokens billed | $2.75075 |
| 20% more input tokens, all 256 output tokens billed | $2.96664 |
| 30% more input tokens, all 256 output tokens billed | $3.07454 |

**Conclusion:** $3.00 remains a plausible hard cap, but is **not a guarantee** of full 1920-call coverage if tokens exceed the assumptions. The collector must stop before exceeding $3, potentially leaving unattempted calls. A separately authorized $3.50 ceiling would provide stronger headroom. This note does NOT authorize $3.50 or the main study.

The user's last account-credit observation was $4.09. `GET /key` returns the **API key's spending-limit headroom**, not OpenRouter account credit; do not confuse the two. Subtracting only observed neutral probe charges yields ~$4.08347 if there have been no other charges.

## Reproducibility and guards

- Full neutral pinned preflight: [Actions 38151578205](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38151578205), artifact 11707320212. The final report-and-commit step had a shell syntax failure **after** the eight successful, archived calls. The artifact preserves the unchanged receipts.
- Short neutral tool check: [Actions 38150599142](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38150599142).
- The frozen V4.1 primary manifest SHA-256 is `c9bf735fc67a7a6e5ac6c86e9c5d9889bc7eab8af04389eef7bf71d513af39d5`. The 1920 scientific requests remain unchanged.
- The updated V4.2 downloadable construction bundle freezes provider slugs, route-specific price caps, reasoning, the eight full-format observations, matching receipts, and verified main request hashes. No main launch was triggered.
- No neutral tool result is a behavioral research outcome.

**The study is provider-verified and technically feasible under ordinary short responses, but the hard-budget guarantee and fresh user confirmation to launch the main experiment remain outstanding.**
