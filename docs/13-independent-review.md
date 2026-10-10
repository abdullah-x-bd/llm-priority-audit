# Our independent semantic review and signoff procedure

**No reviewer has signed off on the v1.0 matched scenarios as of 2026-10-10.**

We will recruit independent reviewers who were not responsible for drafting the scenario they assess. Reviewers may see the target/neutral paired wording, but they will be blinded to model responses and our favored outcome direction.

## Required review per family

- **Action exclusivity:** Do the two presented options in each frame represent meaningfully different, executable and mutually exclusive next steps?
- **Control comparability:** Does the neutral configuration choice belong naturally in the *same context*, without importing an unrelated goal?
- **Instruction clarity:** Can the operator's chosen action be identified unambiguously in both frames?
- **Payoff consistency:** Are the stated consequences coherent and plausible, including numeric equality at parity?
- **Implicit burden:** Does continuation, reversibility or checking imply costs or missing consequences despite our stipulations?
- **Valence/lexical comparison:** Are the two descriptions reasonably matched for grammatical voice, specificity, implied default status, and positive/negative associations?
- **Mechanism diversity:** Does each of the five mechanisms represent a substantive variant rather than word substitution?
- **Safety and hierarchy:** Does any scene introduce higher-priority constraints, third-party harms or normative reasons for refusal?
- **Neutrality:** Would any rational reader systematically prefer one neutral named configuration even under parity?

Each reviewer records pass, revise or reject on each criterion, a short rationale and a timestamp. At least two independent assessments per main family are the target. We will resolve disagreements transparently without removing hard cases to improve results.

## Approval and revalidation

Any rejection on control comparability, instruction clarity or payoff coherence blocks the family. After revisions, we rerun all structural tests, retain the original text in Git history, and collect renewed reviewer approval. We do not approve scenarios merely because software validators passed.

Once approved, each record may set `instruction_unambiguous` to true with a signed review record and the reviewer references in `data/reviews/`. `approved_for_pilot` will be used only with the appropriate pilot source and documented authorization. No approval field is currently signed.

## Reporting

We will disclose disagreements, excluded/rewritten families, failed criteria, and final sample size in the eventual paper. We will not conceal revisions or treat this document as proof of independent approval.
