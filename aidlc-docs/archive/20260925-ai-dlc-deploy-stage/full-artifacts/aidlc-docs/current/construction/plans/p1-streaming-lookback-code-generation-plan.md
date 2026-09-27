# Code Generation Plan: P1 Streaming Lookback

## Unit Context

- **Unit**: p1-streaming-lookback
- **Workspace root**: /Users/carlosdiogo/code_repo/test_aidlc
- **Project type**: Brownfield Databricks workload.
- **Stories**: No separate user-story stage was needed; traceability is to the approved requirements in aidlc-docs/current/inception/requirements/p1-streaming-lookback-requirements.md.
- **Dependencies**: Existing bronze ingestion and CDF enablement precede silver processing; the P1 job already runs bronze before silver.
- **Data contracts**: Kafka source identity (topic, partition, offset); silver current-state identity event_key; quarantine identity (topic, partition, offset). No schema changes.

## Interface Decision: Independent Bundle Parameters

The current Bundle already declares a job-level environment parameter. Databricks Bundle validation does not permit job-level parameters and task-level notebook base_parameters to coexist. Use two distinct job-level parameter keys—bronze_lookback_days and silver_lookback_days—so each task's lookback remains independently overridable while retaining environment as a job-level parameter. Each notebook widget will display the same operator-facing label, **Lookback days**, while using its matching task-specific parameter key. This preserves independent values without task-level base parameters. See [Configure job parameters in Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/job-parameters).

## Expected Interfaces

- Bronze task: bronze_lookback_days, string-valued notebook widget, default "0", visible label Lookback days.
- Silver task: silver_lookback_days, string-valued notebook widget, default "0", visible label Lookback days.
- Job-level defaults: both lookback parameters are "0"; existing environment parameter remains unchanged.
- Positive integer values reset only the selected layer checkpoint and establish that layer's approved source-time cutoff.

## Generation Steps

1. [x] **Update approved requirement/design wording** — record the Bundle-compatible parameter keys while preserving independent layer semantics and the operator-facing widget label. Trace to Requirements 5 and 8 and NFR observability/usability decisions.
2. [x] **Modify `notebooks/P1/bronze/bronze_ingestion.py` in place** — add the bronze lookback widget to the Widgets cell; validate as a non-negative integer before touching checkpoint storage; calculate a single UTC cutoff; for positive values, clear only the bronze checkpoint after prerequisites pass and set Kafka `startingTimestamp`; retain current `startingOffsets` behavior for zero; capture replay observations and emit the structured task-log summary. Keep merge key, `AvailableNow`, and the six-cell order unchanged.
3. [x] **Modify `notebooks/P1/silver/silver_processing.py` in place** — add the silver lookback widget to the Widgets cell; validate before checkpoint operations; calculate a single UTC cutoff; for positive values, clear only the silver checkpoint after table/CDF prerequisites pass and set Delta CDF `startingTimestamp`; retain existing behavior for zero; capture `_commit_timestamp` before dropping CDF metadata and emit the structured task-log summary. Keep silver/quarantine merge semantics, `AvailableNow`, and cell order unchanged.
4. [x] **Update `jobs/P1/resources/p1-daily-pipeline.yml`** — add job-level `bronze_lookback_days` and `silver_lookback_days` parameters, both defaulting to `"0"`; retain the existing environment job parameter and task order. Do not add `base_parameters`.
5. [x] **Update maintained documentation** — update `aidlc-docs/knowledge/p1-databricks-workload.md` with the runtime behavior and independent job parameter keys; update the current code summary. Deploy handoff artifacts will be produced in the Deploy stage.
6. [x] **Review implementation consistency** — inspected widget validation, checkpoint path isolation and reset failure behavior, source options/cutoff formatting, first-observed timestamp reporting, job parameter names/defaults, Google-style docstrings, and six-cell notebook structure. Clarified that connectivity failures may occur after reset and noted the per-batch aggregation overhead. Targeted whitespace review passed; no tests or runtime checks were run.

## Out of Scope

- No schema migration, new tables, libraries, infrastructure resources, or monitoring service.
- No changes to Kafka credentials, environment configuration, output schemas, or replay idempotency keys.
- No live Kafka, Delta, S3 checkpoint, Databricks job, or production execution.

## Plan Approval

Code Generation Part 1 was approved by the user with “pprove & Continue” on 2026-09-25. Part 2 and static consistency review are complete; implementation is awaiting user review. No automated tests or runtime operations were performed.
