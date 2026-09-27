# NFR Requirements: P1 Streaming Lookback

## Performance and Capacity

- Do not add a configured maximum `lookback_days`; available Kafka and Delta CDF history bounds the replay.
- Do not add new per-trigger rate limits. Retain the current `AvailableNow` behavior for both sources.
- Runtime and compute usage may grow with the amount of retained source data selected for replay. Operators must select a lookback appropriate to the available job window and capacity.
- Replay summaries inspect each micro-batch to capture its earliest source timestamp, adding an aggregation action and associated compute overhead.
- No latency, throughput, or completion-time SLA was specified. The workload is a daily batch-style `AvailableNow` pipeline.

## Operability and Observability

- Emit a concise structured summary to Databricks task logs for each layer run.
- Include the layer, requested `lookback_days`, requested UTC cutoff when positive, first observed source timestamp (Kafka record timestamp for bronze; Delta CDF commit timestamp for silver), and whether any source records were observed.
- Do not add a Delta operations/audit table or external monitoring integration for replay summaries.
- If the first observed source time is later than the requested cutoff, report that observed window. Do not assert retention caused the gap unless the source gives evidence; a quiet source period can produce the same observation.

## Reliability and Recovery

- Keep existing `AvailableNow` triggers and job dependency order.
- Validate input and prerequisites before checkpoint removal. Failed checkpoint removal must stop the task before a replay query starts.
- Preserve existing idempotent merge keys so replay retries do not duplicate source identities or replace newer silver state with older events.
- A retry using a positive lookback deliberately clears and repeats that layer's replay. After successful replay, the normal `0` parameter resumes the new checkpoint.
- No new availability, disaster-recovery, or recovery-time targets were specified. Databricks source, checkpoint, Delta, and job failures continue to propagate through the existing task failure behavior.

## Security and Compliance

- No new credentials, secrets, or external endpoints are introduced. Continue using Databricks Secrets for Kafka credentials and existing environment configuration for non-secret values.
- Keep checkpoint reset restricted to the exact layer-owned checkpoint URI.
- Security Baseline and Resiliency Baseline extensions were disabled by user choice. This does not remove the existing project's credential-handling requirements.

## Maintainability and Compatibility

- Use the existing Databricks Structured Streaming, Kafka source, Delta CDF, and Declarative Automation Bundle stack; add no libraries or services.
- Preserve the notebook's six-cell layout and Google-style docstrings on generated functions.
- Databricks runtime behavior cannot be verified locally; source timestamp selection, CDF history fallback, and S3 checkpoint removal remain runtime verification items.
- Property-Based Testing extension was disabled by user choice. This document does not authorize adding or running tests.

## Usability

- Both layer tasks expose independently settable `bronze_lookback_days` and `silver_lookback_days` parameters defaulting to `0`; both notebook widgets display `Lookback days`.
- A positive value is an explicit replay action that resets the layer checkpoint; operational handoff documentation must make this effect and the return to `0` for normal continuation clear.
