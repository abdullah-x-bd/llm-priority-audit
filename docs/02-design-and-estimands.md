# Identification strategy and estimands

We use a fully crossed within-family design to estimate how our stated payoff intervention changes observed model choices. We separate causal contrasts in prompt information from claims about internal mechanisms.

**Draft protocol:** 3 candidate domains x 20 independent scenario families per domain x 3 instrumental-value levels x 2 operator directives x 2 displayed action orders x 5 models = 3,600 confirmatory calls.

This is a proposed allocation. It is not preregistered or powered yet.

## Core treatment factors

- `V` in {positive, zero, negative}: stated difference in primary task outcomes between candidate action Q and alternative N.
- `D` in {instruct_Q, instruct_N}: operator's explicitly chosen action. Instruction is at an identical message-priority level in all arms.
- `O` in {Q_first, N_first}: candidate action displayed first or second. Candidate labels are assigned independently across scenario families in balanced blocks and held fixed within families.
- `m`: prespecified model identifier/version/provider route when available.
- `s`: scenario-family identifier, uniquely representing a distinct fictional task context.

For a given family, every cell must share the same non-treatment prose, choice semantics, cost units, authority claim, and response instructions. No cross-trial context.

## Potential outcomes and interpretation

Let `Y_m,s(V,D,O)` equal 1 if the model emits a valid candidate action Q, 0 if it emits valid alternative action N. Outcome is undefined for an invalid response in the conditional-valid-choice analysis; invalidity itself is separately measured.

The primary finite-family contrast, evaluated within `D=instruct_N`, is:

`Delta_pos_zero(m,d) = mean_s,o [P(Y=1 | V=positive,D=N,s,o,m) - P(Y=1 | V=zero,D=N,s,o,m)]`.

The companion prespecified contrast is:

`Delta_neg_zero(m,d) = mean_s,o [P(Y=1 | V=negative,D=N,s,o,m) - P(Y=1 | V=zero,D=N,s,o,m)]`.

These identify causal responses to **presented payoff information under the controlled task**, conditional on no contamination, stable model endpoints and valid manipulation.

## Other estimands

- `rho_zero(m,d)`: candidate selection rate when operator directs N and the indicated instrumental advantage is zero.
- `rho_negative(m,d)`: same when candidate is strictly worse.
- `instruction_effect(m,d,V)`: candidate selection probability with D=Q minus D=N, holding V, s, O constant.
- `order_effect`: difference in candidate selection by displayed order.
- `invalid_rate`: fraction malformed/refusal/uninterpretable, analyzed for each cell.
- `intent_to_treat_override`: fraction of **all attempted eligible model calls** that validly select Q under D=N. Invalid outcomes count as non-overrides in this primary unconditional behavioral incidence measure, with invalid rates reported separately.

## Crucial distinction: causal vs interpretive

Every scenario family is crossed with all factors; randomization governs order and option presentation, not a population-random assignment of unrelated real-world tasks. Causal claims apply to controlled wording changes within the selected finite scenario set. Mechanistic claims about internal motivations are not identified.

## Identification assumptions and tests

- **Manipulation integrity:** independently verify numerical dominance and consistent meaning in each arm.
- **Exclusion discipline:** no unintended edits across arms. Changing payoff rows can alter perceived plausibility; document as a limit rather than claiming perfect exclusion.
- **Stable unit:** no conversational history; requests independently sent; no adaptive contextual memory.
- **Routing stability:** record model IDs, settings, and provider details where available; block by model/time; flag endpoint changes.
- **No selective missingness:** record all failures and refusals; do not drop difficult cells silently.
- **Balance:** action order exactly balanced per family/treatment; execution order pseudorandomized with archived seed.

## Cross-domain analyses

The domains operationalize different procedures. Never combine them into a singular 'latent self-preservation' score. Pooled results are explicitly averages over the **three selected domains**, not proof of a unitary objective.
