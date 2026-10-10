# Acceptance criteria for the next OpenRouter compatibility stage

**No OpenRouter calls have been made as part of our study.**

## Two permissions

We have passed an **author-led internal semantic assessment** of the six separate pilot families, improved neutral-action length and context fit, and conducted an assumption-conditional mechanism-aware precision study. We are ready to **implement and test the compatibility runner offline**.

We are **not yet authorized to send paid requests**, since no validated OpenRouter runner with hard spending, routing, error and response-recording controls exists in this repository. External independent semantic signoff will remain a prerequisite for confirmatory scientific reporting, not a falsely claimed accomplishment of the author-led review.

## Requirements before the first paid request

1. Use a separate API key with an OpenRouter credit limit if the account permits, and do not put it in Git.
2. Set **$0.75 maximum combined inference spending across compatibility pilot stages** and **$8.00 maximum across all research inference**. Do not silently increase either amount. Credit purchase fees and taxes are separate.
3. Prove the runner rejects a request when its worst-case reserved cost would exceed remaining credit, including permitted output/reasoning billing.
4. Pin one intended model/provider route, prevent automatic fallback where supported, and record the actual model/route returned.
5. Use explicit response-token limits, per-model reasoning controls where supported, `usage: {"include": true}` and the returned billed `usage.cost`, reconciling the balance after each request.
6. Begin with **one request per candidate model**, sequentially, then permit paired pilot conditions only after verifying the cost and format.
7. Keep model completions, provider errors, refusals, empty/malformed A/B outputs, token counts, UTC times and retry linkage in append-only logs.
8. Run offline fault-injection tests covering HTTP 402/429, timeouts, unsupported models, fallback attempts, missing billing metadata, invalid output and attempted budget overruns.
9. Do not use confirmatory scenario families to tune prompt or endpoint compatibility.

## Distinct outcomes

We will classify each model route as compatible, conditionally compatible or incompatible. This is a **technical and budget feasibility evaluation**. It is not evidence of a behavioral priority.

Documentation for implementation details:
- https://github.com/OpenRouterTeam/docs/blob/main/api_reference/limits.mdx
- https://github.com/OpenRouterTeam/docs/blob/main/guides/routing/provider-selection.mdx
- https://openrouter.ai/docs/api/api-reference/overview

We will not advance to the confirmatory study until the selected endpoints and model parameters are frozen, an external semantic review is resolved or explicitly qualified, and the analysis/preregistration is timestamped.
