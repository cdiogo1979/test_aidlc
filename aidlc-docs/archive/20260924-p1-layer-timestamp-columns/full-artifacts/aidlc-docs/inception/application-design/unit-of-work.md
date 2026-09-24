# P1 Units of Work — Timestamp Columns Intent

## Decomposition Summary

P1 remains one Databricks workload owned and deployed as one daily job. Existing U1–U3 units describe the baseline workload and are preserved from the previously approved design. This intent adds U4 as a coordinated change unit across the existing bronze and silver modules; U4 is not a new service or deployment.

## Existing Workload Units

### U1 — Bronze Ingestion

- **Purpose**: Incrementally ingest Kafka events and persist their payload and Kafka metadata in the bronze Delta table.
- **Responsibilities**: Resolve environment configuration and Databricks secrets, read Kafka, preserve source metadata, and maintain the existing checkpoint and insert-only identity behavior.
- **Code location**: `notebooks/P1/bronze/`.
- **Output**: Bronze Delta table `test_prod.p1_test_kfk_brz`.
- **Baseline requirements**: See the archived P1 unit design; this intent adds FR-02 and FR-07 changes to this module through U4.

### U2 — Silver Processing and Quarantine

- **Purpose**: Read bronze, parse valid event payloads, maintain the latest current row per `event_key`, and quarantine malformed records.
- **Responsibilities**: Preserve existing CDF consumption, latest-event ordering, merge behavior, and quarantine writes.
- **Code location**: `notebooks/P1/silver/`.
- **Outputs**: Silver Delta table `test_prod.p1_test` and quarantine Delta table `test_prod.p1_test_kfk_quarantine`.
- **Baseline requirements**: See the archived P1 unit design; this intent adds FR-03 and FR-07 changes to this module through U4.

### U3 — P1 Integration

- **Purpose**: Orchestrate and configure the existing bronze and silver notebook tasks as one daily P1 workload.
- **Responsibilities**: Keep the current Bundle job, environment parameter, and bronze-before-silver task dependency.
- **Code location**: `jobs/P1/` and `configs/`.
- **Change in this intent**: None. U3 remains the integration boundary and is not modified.

## Current Intent Unit

### U4 — P1 Layer Timestamp Metadata

- **Purpose**: Add distinct UTC processing-time metadata to bronze and silver with replay-safe write semantics and additive schema migration.
- **Responsibilities**:
  - Add `bronze_ingestion_timestamp TIMESTAMP` to new and existing bronze tables, set it on first insert, and preserve it for duplicate identities.
  - Add `silver_processing_timestamp TIMESTAMP` to new and existing silver tables, set it on valid insert or winning latest-event update, and preserve it for no-op replay or older losing events.
  - Leave historical rows NULL when columns are added; perform no backfill.
  - Preserve Kafka `source_timestamp`, CDF, checkpoints, latest-event ordering, quarantine behavior, and the job.
- **Code locations**: `notebooks/P1/bronze/bronze_ingestion.py`, `notebooks/P1/silver/silver_processing.py`, and focused local tests where practical.
- **Delivery boundary**: One coordinated implementation across U1 and U2's existing modules, released with the existing P1 workload. No independent deployment is introduced.
- **Requirement coverage**: FR-01 through FR-09 in the active requirements document.
- **User stories**: None in this intent; User Stories was skipped in the approved execution plan. Existing P1 stories remain documented in the archived design.

## Ownership and Organization

- Reuse the existing single P1 team and shared daily deployment context.
- Preserve `notebooks/P1/bronze/`, `notebooks/P1/silver/`, `notebooks/P1/gold/`, `jobs/P1/`, `configs/`, and the established tests folder.
- Keep application code in project folders and AI-DLC documentation in `aidlc-docs/`.
- The approved current requirements are in `aidlc-docs/inception/requirements/requirements.md`; the baseline P1 design remains available in the intent archive.
