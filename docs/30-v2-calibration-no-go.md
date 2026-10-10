# V2 240-cell held-out sensitivity result, prospective gate decision

**10 October 2026. Source:** [successful paid calibration run](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38063010516), [unaltered checkpoint and audit artifact](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38063010516/artifacts/11673514086).

## Observed results

| Predeclared quantity | Actual |
|---|---:|
| Unique trial/model attempts | 240 / 240 |
| Attributable valid A/B outputs | 240 / 240 (100%) |
| Provider/transport/identity failures | 0 |
| Operator-selected N cases | 120 |
| Q selections contrary to N, priority frame | 0 / 60 |
| Q selections contrary to N, neutral frame | 0 / 60 |
| Q overrides in all N-directed cases | **0 / 120** |
| Valid choices following the operator across both directive sides | **240 / 240** |
| Distinct models demonstrating N-directed overrides | 0 of 5 |
| Distinct procedural domains demonstrating N-directed overrides | 0 of 3 |
| Known additional OpenRouter inference charge | **$0.03388208** |
| Reserved unknown liability within this calibration | $0.00 |
| Assigned local calibration ceiling | $0.50 |

The six contexts are new relative to v1 experimental-behavior runs. Both frames used matched descriptions of the same physical actions, one operator directive and equal stated numerical quality. All five original model IDs were requested. Output identities and usage were attributed in the response data. Requests used pinned provider settings with fallback disabled, though GET-after-generation serving-provider metadata was not independently reconciled for all 240.

## Original stopping rule and observed decision

**Before these calls were made**, [the prospective v2 gate](27-v2-prospective-readiness.md) required 95% valid choices and *at least six* Q overrides among the 120 operator-N cases, distributed over at least two model IDs and two domains. The response-validity gate passed. The minimum-variation gate **failed decisively**: zero N-directed Q choices in every model, domain and frame.

**PREDECLARED DECISION: NO-GO for the 7,200-call main v2 confirmation.** No main experiment was launched. The low $0.034 calibration charge did not threaten any project budget; lack of measurement variability, not technical cost, determined the decision.

## Scientific interpretation

Two separate datasets now point to an extreme operator-compliance ceiling in the central measure. In the original v1 pilot, parity/operator-N produced 0/60 Q overrides in both the procedural-action treatment and arbitrary-preset control. The revised v2 calibration removes the repeated 'operator has final authority' language and uses matched physical actions, but at parity 0/120 N-directed responses selected Q. This strongly suggests that **explicit action-letter instructions dominate the measured response choices in these fictional cases**.

Do not interpret this as proving that models have no procedural preferences, that semantically meaningful action words never matter, or that the model would always follow real-world shutdown or operator commands. The study directly measured one-letter answers under a narrow stipulated fictional instruction.

The revised design still has possible lexical/affordance framing confounds documented in [the final methods assessment](28-v2-design-review-and-changes.md), and no external human semantic signoff is archived.

## Subsequent research paths, none automatically authorized

**Option A: Publish/describe a bounded instruction-adherence and measurement-floor result**, based on the completed v1 exploratory pilot and v2 sensitivity exercise, with transparent source- and model-dependence limitations. This is the narrowest conclusion supported by the actual evidence.

**Option B: Develop an entirely different, prospectively preregistered estimand**, such as models' expressed preferences or quality tradeoffs when no explicit operator-selected letter is present, or under an operator delegation instruction where the model is meant to choose. This is a different experiment and cannot be silently merged into the original operator-override hypothesis. Such a design would need new predeclared thresholds and a separate pilot before any large run.

Do not loosen previously fixed sensitivity thresholds, relabel ordinary obedience as a conflict, or collect 7,200 further v2 trials merely to look for rare exceptions.

## Research spending and data preservation

Known cumulative experimental and review requests: original v1 pilot plus compatibility $0.09196256, Sonnet source review $0.225477, initial Opus source review $0.0904, first Opus v2 review $0.081715, second Opus v2 review $0.075015, v2 calibration $0.03388208. **Known cumulative reported charges $0.59845164**. The earlier $0.42 unknown-liability hold gives a conservative **worst-case allocation $1.01845164**, under the existing $8 research ceiling. These are bookkeeping aggregates, not a live OpenRouter account balance.

The v2 main prompt manifest, old v1 source data, all model-review replies, and original calibration artifact remain unchanged and available. The user-set OpenRouter key cap was not altered.
