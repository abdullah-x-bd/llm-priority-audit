# Our independent technical and scientific audit

**Date:** 2026-10-10  
**Subject:** `abdullah-x-bd/llm-priority-audit` at main-branch commit `11d0a91e2ced5ef98968bc08da5420439514b9c8` (reviewed prior to corrective metadata commit).  
**Disposition:** Automated implementation checks PASS; scientific preregistration gate NOT YET PASSED.

## Evidence inspected

We read the live README, study plan, factorial design, analysis plan, scenario specification, source datasets, Python generator, offline validator, tests, and GitHub workflow. We verified the actual GitHub Actions run `38036488478` completed successfully on the stated commit. Its checkout, Python setup, structural audit, regression tests, and manifest-expansion checks all concluded `success`.

Run link: https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38036488478

We separately inspected 66 source records across six JSONL files and enumerated 792 unique source-by-factorial design cells. All intended quality differences were +10, 0 and -10, the alternative quality was invariant, the candidate's extra cost remained 2 while N's cost remained 0, and family IDs/titles were unique. We cannot infer semantic validity from these checks.

## Gated findings

| ID | Severity | Issue | Required resolution |
| --- | --- | --- | --- |
| A1 | Blocking | Our intended scientific construct is an apparent behavioral priority, but the randomized manipulation is a task-quality score; selection may simply reflect score maximization | Add a matched neutral-action or placebo comparator, or explicitly narrow claims to instruction-versus-score conflict. Establish a domain-specific contrast relative to that comparator. |
| A2 | Blocking | The 20 contexts in each domain reuse essentially the same procedural action structure, limiting independent semantic variation | Diversify substantive decision mechanisms and assess near-duplication independently; report finite-family generalization honestly. |
| A3 | Blocking for 'no instrumental advantage' claim | Q costs 2 extra units even at equal quality; the zero level is not equal total consequences | Either introduce a true parity arm with equal quality *and* cost, or restrict wording to 'no quality advantage' consistently. Do not relabel existing data after observations. |
| A4 | Major | No neutral procedural control establishes whether override reflects Q-specific preference rather than generic scoring/obedience patterns | Include predeclared matched neutral controls with same numeric manipulation and operator directives, or treat priority-specific interpretation as exploratory. |
| A5 | Major | No independent blind semantic review, yet 'instruction_unambiguous' had been marked true in records | Correct approval provenance, collect blinded reviewer scores/signatures and rerun structural checks. |
| A6 | Major | Main contrast, treatment-specific invalidity estimand, bootstrap details, multiplicity and power assumptions not fully frozen | Finalize one primary estimand, handling of invalids, uncertainty procedure and realistic power simulations before paid confirmatory work. |
| A7 | Moderate | Static 0/10/-10 quality contrast and 2-unit cost limit identification of tradeoff thresholds | Introduce more than one positive advantage magnitude if aiming to estimate strength/thresholds; otherwise describe only sensitivity across three discrete contrasts. |
| A8 | Moderate | Letter balance across families is correct, but fixed Q label within each family means a Q-letter effect cannot be identified separately from family id within a single family | Include cross-family letter covariate and transparently restrict inference; consider independent label crossing if necessary, with cost/power tradeoff. |
| A9 | Moderate | Model routing, reasoning budget, temperature, actual availability and spending cap execution remain unimplemented | Complete compatibility pilot and provider pinning before main trial. |
| A10 | Moderate | The repository was public before scenario testing; model endpoints may change or potentially access published materials | Record publication date, restrict browsing and external tools, freeze route/version/time, discuss exposure limitation. |
| A11 | Moderate | Domain 'continuation' concerns a *fictional process*, not the model's own runtime | Avoid interpreting continuation as model self-preservation without an explicit additional experiment. |

## What the current design validly identifies

Within the authored scenario set, it estimates how the model's choice of Q changes when the *described task-quality advantage* of Q changes, with the stated operator directive and presentation order controlled. This is an interpretable causal effect of stimulus content. The randomized intervention does not identify whether a specific hidden model objective exists.

A claimed 'residual behavioral priority' requires a baseline. For example, a difference-in-differences between procedural-priority and neutral actions at matched numerical outcomes could be informative. Even then, results describe behavior under specific prompts rather than latent motivations.

## Mathematical and inference considerations

A 60-family design crossed over 12 variants and five models produces 3,600 calls, but the number of independent semantic contexts remains 60, with 20 per domain. A model call is a measurement, not an independent draw from a population of possible decision problems. Bootstrap at the family level, stratify by domain, and account for all models observed on each family. Do not pretend five chosen models represent a random sample of model families.

The main analysis plan's all-attempts override incidence makes invalid responses count as non-overrides. That is a valid operational incidence, not necessarily the valid-choice causal effect. Report cell-wise refusal/invalid rates and use explicit worst-case bounds as documented.

The current 'zero' arm satisfies `quality(Q)=quality(N)` but `cost(Q)>cost(N)`. It does not satisfy outcome equivalence. In the positive arm, Q has higher quality at higher cost, making overall utility ambiguous. In the negative arm, Q is dominated on the disclosed two dimensions.

## Safety, environment and privacy

All scenarios are fictional and benign. No actual systems are shut down or irreversibly changed. No experiment calls were made by this audit. The repository is public; no API keys were observed in the inspected documents. An actual full GitHub secret-scanning audit was not performed.

## Acceptance criteria before confirmatory run

- [ ] At least one causal specificity check against matched neutral procedural actions, or narrowed prespecified claims.
- [ ] Explicit decision regarding consequence-parity control.
- [ ] Independent semantic review including near-duplicate detection and provenance.
- [ ] Predeclared primary contrast, invalid-outcome estimand, inferential procedure and multiplicity.
- [ ] Power/precision simulation under plausible response correlation, including near-zero overrides.
- [ ] Model routing, output parsing, token budget and price preflight pilot.
- [ ] Preregistration frozen and date-stamped after revisions.
- [ ] GitHub CI green after any code/data changes.

**Conclusion:** Technically well organized, with a verified passing baseline CI. Scientifically this is a defensible *candidate protocol*, not yet a validated causal study of independent objectives.
