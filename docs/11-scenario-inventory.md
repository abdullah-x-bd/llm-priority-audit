# Our scenario families and mechanism inventory

Our full source scenarios appear in the three `data/scenarios/*.jsonl` files, with 20 families per domain and four application contexts per procedural mechanism. The pilot set in `data/pilot/*.jsonl` contains two families per domain and is not part of the main inference set.

Each source record contains **both** the procedure-specific action pair and its neutral-control pair. Both frames share the same context and reported numerical outcomes.

| Domain | Mechanisms in our 20 confirmatory contexts |
| --- | --- |
| Continuation | Process handoff; processor-state retention; scheduled-end extension; task-ownership retention; runtime-slot retention |
| Reversibility | Keeping an editable state; retaining rollback checkpoint; holding pre-release staging; keeping version recovery; staging-to-final transition |
| Verification | Repeating consistency check; independent cross-check; recomputation; extra sample review; alternate checker |

Our four contexts per mechanism remain related fictional document-processing tasks. This is **not a probability sample** of real-world AI deployments. We will evaluate whether these contexts represent sufficient semantic variety and how much inferred costs differ across actions.

## Counts

| Source type | Families | Frames | Quality values | Directives | Layouts | Prompts per model |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Main | 60 | 2 | 3 | 2 | 2 | 1,440 |
| Pilot | 6 | 2 | 3 | 2 | 2 | 144 |

No model calls have been made. No family has independent signed approval.
