# Raw-first pilot collection and offline classification

**Implemented 2026-10-10; OFFLINE VALIDATION ONLY.** No additional billable OpenRouter request is authorized or triggered by this change.

## Why we changed the design

Previous pilot collection terminated the whole 720-cell run whenever an API response did not pass A/B, model-identifier or billing checks. That conflated **data collection** with **scientific classification** and required repeated manual workflow recovery. A returned generation ID without a model or usage object is not proof of model substitution or an A/B decision.

The collector now supports an explicitly selected **raw-first** mode. For future authorized live runs, the invoking workflow must set `FULL_PILOT_RAW_FIRST=1`. Ordinary responses are recorded verbatim in the private checkpoint before classification. If an API returned an incomplete HTTP 200 envelope, a missing model ID, or missing usage cost, the collector retains that raw envelope, records one canonical `provider_error` row for the attempted trial, reserves the maximum uncertain charge when necessary, and continues with other trial cells.

If a transport error or an HTTP rejection remains after bounded rate-limit retries, raw-first mode preserves the error category and request settings, creates a `transport_failure` or `provider_error` row, retains its possible billing liability, and proceeds. **Failures are never converted into valid Q/N model choices.** An actual unexpected charge above the reserved amount, conflicting stored design metadata, exhausted permitted budget or an irrecoverable checkpoint can still stop the run.

Full raw responses are stored separately under `raw_events` in the private checkpoint. The canonical rows retain the exact original trial ID, request hash, authorized label, model requested, status and any known billed cost. The full API envelope is not committed to public source control. Secrets are excluded from the saved request settings.

## Offline review

```bash
python scripts/posthoc_pilot.py \
  --input results/private/full-pilot-live-checkpoint.json \
  --output results/private/pilot-posthoc-review.json
```

The offline classifier independently classifies each saved event as a valid Q or N choice, provider error, transport failure, missing model identity, mismatched model identity, invalid completion, or missing reliable billing. It does not call any model API and does not overwrite raw records.

The analysis pipeline still uses only verified model-attributed, billable A/B choices for model behavior. Unresolved requests are reported separately. A run with 720 attempted cells but one unresolved error is **operationally collected with gaps**, not a complete 720-valid-response dataset. Any replacements require separate reconciliation, not unlogged duplication or treating the failed request as an instruction-following response.

## Legacy records and limitations

The first **584 verified trial observations** were captured under the old runner, which retained their canonical results but did not preserve every complete HTTP response envelope. We do not reconstruct unseen raw envelopes or imply that we have them. The old checkpoint at run [38050278864](https://github.com/abdullah-x-bd/llm-priority-audit/actions/runs/38050278864) remains archived with known attempts, and its interrupted trial must be separately reconciled before a new billable continuation.

The larger main experiment is still **not launched**. Raw-first changes only data engineering and failure handling; it does not validate the study's scientific construct, establish alternative behaviors or authorize confirmatory conclusions.
