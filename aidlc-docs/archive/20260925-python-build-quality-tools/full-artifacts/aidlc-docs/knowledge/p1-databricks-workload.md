# P1 Databricks Workload

## Purpose and scope

P1 ingests JSON events from Kafka into bronze Delta, quarantines malformed messages, and maintains the latest valid event per `event_key` in silver. Gold processing remains out of scope.

## Canonical design documents

- [P1 application design](P1/application-design.md): architecture, component boundaries, interfaces, orchestration, and dependencies.
- [U1 Bronze Ingestion functional design](P1/functional-design/U1-bronze-ingestion.md)
- [U2 Silver Processing and Quarantine functional design](P1/functional-design/U2-silver-processing-and-quarantine.md)
- [U3 P1 Integration functional design](P1/functional-design/U3-p1-integration.md)
- [U4 P1 Layer Timestamp Metadata functional design](P1/functional-design/U4-p1-layer-timestamp-metadata.md)

These are the canonical approved design summaries. Intent-specific source artifacts remain in their immutable archives.

## Architecture and contracts

- `jobs/P1/` contains the authoritative Databricks Declarative Automation Bundle. Its daily job runs bronze before silver. Both tasks receive the shared `environment` parameter and independent `bronze_lookback_days` / `silver_lookback_days` job parameters, each defaulting to `0`.
- `notebooks/P1/bronze/bronze_ingestion.py` reads Kafka incrementally with Structured Streaming `AvailableNow`, uses `{data_path}/checkpoints/P1/bronze_ingestion`, and inserts records keyed by `(topic, partition, offset)` into `<database>.p1_test_kfk_brz`. A zero lookback resumes the checkpoint; a positive `bronze_lookback_days` clears the bronze checkpoint and begins from the Kafka record timestamp cutoff.
- Bronze Change Data Feed is enabled for silver consumption. `notebooks/P1/silver/silver_processing.py` reads CDF with `AvailableNow` and uses `{data_path}/checkpoints/P1/silver_processing`. A zero lookback resumes the checkpoint; a positive `silver_lookback_days` clears the silver checkpoint and begins from the bronze CDF commit timestamp cutoff.
- Each notebook validates its lookback as a non-negative integer before checkpoint access, reports the requested cutoff and earliest observed source timestamp in task logs, and uses its own checkpoint. Positive values intentionally repeat the replay if submitted again; normal continuation uses zero.
- Silver maintains the latest valid event per nonblank `event_key` in `<database>.p1_test`; non-key JSON properties are stored as `VARIANT`. Malformed payloads and invalid keys go to `<database>.p1_test_kfk_quarantine` with source metadata and diagnostics.
- Latest-event ordering remains Kafka `source_timestamp`, then partition and offset. Silver and quarantine writes are separate idempotent Delta operations, not a cross-table transaction.
- The existing silver `VARIANT` implementation requires Databricks Runtime 15.4 LTS or later.

## Layer processing timestamps

The timestamp-columns intent adds `bronze_ingestion_timestamp TIMESTAMP` to bronze and `silver_processing_timestamp TIMESTAMP` to silver. They are distinct UTC processing instants; Kafka `source_timestamp` remains source event time. Bronze records the timestamp on first insertion; silver records it on an accepted current-state insert or winning update. Duplicate or no-op replay does not refresh a committed value.

The implementation adds missing nullable columns before writes and leaves historical records NULL. `src/delta_schema.py` contains the shared schema migration/type-validation helper. No timestamp was backfilled and no live table was migrated.

## Configuration and security

`configs/{environment}.yaml` supplies environment-specific settings. The current `prod.yaml` has database `test_prod`, data path `s3://test_prod`, Kafka host `test.com:9995`, topic `my-topic`, and secret key name `my-secret`. Kafka username and Databricks secret scope remain deployment inputs. Password material belongs only in Databricks Secrets. Never use production to test this workload.

The `prod` bundle target still requires deployment-provided schedule/timezone, compute policy/runtime, run-as service principal, and retry values. Required permissions include Kafka topic and secret access, checkpoint/storage access, bronze CDF reads, and silver/quarantine writes.

## Verification and release status

For intent `20260924-p1-layer-timestamp-columns`, all 22 local unit tests passed and Python syntax checks passed for four changed files. The user explicitly accepted a verification waiver because no Databricks environment is available. Delta schema migration against live tables, CDF compatibility after schema evolution, notebook execution, UTC session behavior, Kafka integration, and job execution remain unverified. No job was deployed and no notebook or production data was run. The waiver is not evidence of runtime success or production readiness.

The current lookback implementation has not been run in Databricks. Kafka timestamp selection, CDF history fallback, Bundle parameter delivery, S3 checkpoint listing/removal, and notebook execution remain unverified. The previous P1 workload intent and its separate verification waiver are summarized at `aidlc-docs/archive/20260924-p1-databricks-workload/intent-summary.md`.

Before release, supply deployment values through the approved non-secret mechanism, validate the Bundle in an authorized workspace, and run P1 integration and performance checks in an isolated non-production Databricks environment. Monitoring, alerting, incident response, rollback, maintenance, and on-call procedures still require owner decisions.
