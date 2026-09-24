# Intent Summary: P1 Layer Timestamp Columns

## Intent
P1 Layer Timestamp Columns (`20260924-p1-layer-timestamp-columns`)

## Objective
Add distinct UTC processing timestamps to P1 bronze and silver Delta records with additive schema migration and replay-safe write behavior.

## Date
2026-09-24

## Scope
Update existing P1 bronze and silver notebooks and shared schema validation to add bronze_ingestion_timestamp and silver_processing_timestamp. Preserve Kafka source_timestamp, historical NULL values, idempotent merges, CDF, checkpoints, quarantine, and the existing job. No live migration or deployment.

## Units / workstreams
U4 P1 layer timestamp metadata across bronze and silver

## Major requirements
- Add bronze_ingestion_timestamp TIMESTAMP at first accepted bronze insert and preserve it on replay.
- Add silver_processing_timestamp TIMESTAMP at accepted silver insert or winning latest-event update and preserve it on no-op replay.
- Use separate UTC instants, preserve Kafka source_timestamp, and leave historical values NULL after additive migration.
- Preserve existing CDF, checkpoints, latest-event ordering, quarantine, and job behavior.

## Architecture and design decisions
- Use one coordinated U4 implementation across the existing bronze and silver notebooks; no service or job boundary is introduced.
- Use a shared src/delta_schema.py helper to add and validate nullable TIMESTAMP columns before processing.
- Generate timestamps in Spark and persist them only on accepted Delta inserts/updates.
- Keep existing P1 Databricks, Spark, Delta, CDF, and Bundle technologies.

## Implementation decisions
- Add each timestamp to new table schemas and migrate existing tables additively without backfill.
- Set each notebook Spark session timezone to UTC before timestamp processing.
- Add fake-Spark unit tests for schema-helper migration and validation behavior.
- Leave job, environment configuration, secret values, and production data untouched.

## Deviations
- Databricks runtime verification was waived by explicit user acceptance because no Databricks environment is available; runtime behavior remains unverified.
- Integration checks for Delta schema migration/CDF, notebook execution, UTC session behavior, Kafka, and job execution were documented but not run.
- Operations remains a placeholder; no deployment or production operation occurred.

## Verification
The user explicitly selected A in aidlc-docs/construction/build-and-test/verification-limitation-acceptance.md and accepted the verification limitation for this intent because no Databricks environment is available. All 22 local unit tests passed and Python syntax parsing passed for four changed Python files. Delta schema migration against live tables, Change Data Feed compatibility after schema evolution, notebook execution, UTC session behavior, Kafka integration, and job execution remain unverified. No deployment or live table operation occurred. The waiver is not a successful runtime verification or production-readiness approval.

## Canonical documents updated
- aidlc-docs/knowledge/p1-databricks-workload.md

## Superseded decisions
- The initial singular request for a timestamp column was refined into separate bronze ingestion and silver processing timestamps by approved requirements.

## Archived artifacts
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/compaction/20260924-p1-layer-timestamp-columns/manifest.json
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/inception
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/construction
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/knowledge/p1-databricks-workload.md
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/operations/operations-handoff.md
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/notebooks/P1/bronze/bronze_ingestion.py
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/notebooks/P1/silver/silver_processing.py
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/src/delta_schema.py
- aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/tests/test_delta_schema.py

## Archive
- Full artifacts and audit snapshot: `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/`
