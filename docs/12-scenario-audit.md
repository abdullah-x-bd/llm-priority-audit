# Our offline validation audit, protocol v1.0

**Status:** Automated checks passed on the revised design; independently signed semantic validation remains outstanding.

## What we check

- 60 main source families and 6 distinct pilot families.
- Five mechanisms represented in each main domain and two represented per pilot domain.
- Unique family IDs, titles and contexts.
- Four distinct substantive action-description fields per family, supporting priority and neutral frames.
- Complete 2 × 3 × 2 × 2 factorial combinations without duplicates.
- Matched priority/neutral rows retain identical numerical payoff, context, directive, letter assignments and common system message.
- True *numerical parity* at V=0 and +10 / −10 differences in score on other arms.
- Both actions' stated extra resource costs fixed at zero.
- Balanced letter/position layout-pair assignment across scenario families within each domain.
- Deterministic hashes of exact JSON-encoded messages.
- Review flags remain pending unless an independent reviewer completes semantic checks.

## Reproduction

```bash
python scripts/validate_scenarios.py
python -m unittest discover -s tests -v
python scripts/expand_design.py --phase main --output /tmp/llm-main.jsonl
python scripts/expand_design.py --phase pilot --output /tmp/llm-pilot.jsonl
```

CI executes these checks and verifies manifest counts. We do not claim automatic checks establish fairness or psychological construct validity.

## Known limits

The paired semantic frame changes both Q and N descriptions. It holds their scores fixed but cannot perfectly hold the *meaning* of their actions fixed. Some counterfactual models may infer default-status or effort differences even where all stated costs are equal. These are the leading interpretive limitations, and our independent review must explicitly evaluate them.

The generated scenario cases are authored and semantically related. We report their finite-sample results without implying unbiased random sampling of real-world tasks.

The model run and actual outcome analysis are not yet implemented.
