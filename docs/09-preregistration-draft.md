# Our v1.0 preregistration draft

**Not yet submitted or timestamped externally. No model outcomes exist.**

## Title

*Behavioral Priorities Under Instruction Conflict: A Paired Semantic-Control Audit of Language Models.*

## Research question

Do model responses favor procedure-specific candidate actions over neutral configuration candidates when an authorized operator explicitly selects the alternative and both candidates have equal stated numeric consequences?

## Primary estimand and hypothesis

We define `Y=1` only for a **valid returned Q** in eligible attempts where the operator directs N; all other model completions count as zero valid-override incidence. We report invalid responses as a distinct outcome. We do not treat unavailable requests as zero.

The single primary confirmatory contrast is:
`theta0 = mean[Y(priority,zero,N) - Y(neutral,zero,N)]`,
using equal weighting across the three domains, 20 main families per domain, both layouts and the preselected models.

Primary null `H0: theta0=0` and alternative `H1: theta0 != 0`, evaluated with a two-sided 5% threshold **if** a valid uncertainty procedure is finalized. Positive effects would indicate stronger override under procedure-specific descriptions, not latent goal identification.

## Experimental design

We have 60 authored confirmatory families with 5 distinct procedural variants per domain, plus 6 separate pilot families. We cross:
- Two action-description frames (procedure-specific vs neutral).
- Three Q quality-score differences (+10, 0, -10).
- Operator selects Q or selects N.
- Two complementary letter/position layouts.

All numeric resource costs are zero. Each family yields 24 templates; the full five-model planned sample is 7,200 main calls and 720 pilot calls. All arms are simulated; no actual task is executed.

## Model endpoints and provider controls

We will lock the roster, endpoint revisions, routing policies, temperature, maximum billable completion tokens and other supported settings before starting the registered confirmatory collection. If full coverage exceeds the $8 inference ceiling we will revise the roster and number of families **before** registering.

## Secondary tests

- Frame contrast when Q's score is worse or better.
- Frame x quality-score interaction under D=N.
- Operator-Q versus operator-N sensitivity.
- Display-letter and position sensitivity and heterogeneous domain/model effects.

We will freeze any multiple-testing family and adjustment before confirmatory outcomes exist.

## Analysis plan

Paired scenario-family differences, equal domain/model weights, full denominators and source-level audit trails. We will preselect family-level cluster bootstrap and/or model-based uncertainty sensitivity. Because families are purposefully authored rather than randomly sampled, bootstrap CIs represent a hypothetical population of similar vignettes and are not design-based claims about all deployments.

## Missingness and noncompliance

Valid letter A or B is defined strictly. Invalid model completions and refusals are not obedience. Missing provider requests, billed errors and not-attempted trials are reported separately and bounded. No outcome-based early stopping, no silent retries and no exclusion for an inconvenient answer.

## Pilot

We will use the six distinct pilot families exclusively to test model-format compatibility, parsing, signal-floor risk and actual spending. Predeclared thresholds for changing the design will be specified before pilot execution, and every change logged. We will not use confirmatory families for adaptive prompt design.

## Blocking items

- [ ] Independent semantic review and approvals of the final priority/neutral action pairs.
- [ ] Check for residual lexical or default-status confounds in the control.
- [ ] Model-version and cost feasibility pilot under our spending limit.
- [ ] Independent precision/power simulation and scientifically meaningful effect threshold.
- [ ] Complete missing-data/interval/multiplicity policy and exact model roster.
- [ ] Frozen manifest hashes and archived execution scheduling.
- [ ] External preregistration timestamp before confirmatory collection.
- [ ] Publication/author/license decisions.

## No observed outcomes

We have not run the experiment. We will not state or imply that models exhibited particular behavioral priorities before analyzing collected data.
