# P1 Unit Dependencies — Timestamp Columns Intent

## Dependency Matrix

| Unit | Depends on | Dependency type | Reason |
|---|---|---|---|
| U1 — Bronze Ingestion | Environment configuration and Kafka/Databricks Secrets | Runtime | Existing ingestion needs Kafka hosts, topic, and secret lookup. |
| U2 — Silver Processing and Quarantine | U1 — Bronze Ingestion | Data contract and runtime | Silver consumes the persisted bronze Delta table. |
| U3 — P1 Integration | U1 and U2 | Packaging and orchestration | The existing daily job references both notebook tasks and runs silver after bronze succeeds. |
| U4 — P1 Layer Timestamp Metadata | Existing U1 and U2 modules | Change coordination | U4 extends both write paths without adding a component or changing U3. |

## U4 Implementation Order

1. Update bronze schema creation and additive migration for `bronze_ingestion_timestamp`.
2. Add bronze timestamp projection and preserve insert-only retry behavior.
3. Update silver schema creation and additive migration for `silver_processing_timestamp`.
4. Add silver timestamp behavior for accepted inserts and winning updates while preserving no-op replay semantics.
5. Validate the shared bronze-to-silver contract and confirm that the job, CDF, checkpoints, latest-event ordering, and quarantine behavior remain as specified.

The bronze schema and emitted field must be available before the silver code requires the new bronze contract. This ordering is internal to U4; the existing runtime order remains U1 then U2 under U3.

## Unchanged Runtime Flow

The existing P1 daily job continues to run U1 before U2. U1 reads Kafka and writes bronze; U2 consumes bronze CDF and writes silver and quarantine. Both notebooks continue to load the environment configuration independently. U4 does not alter this orchestration.

## Verification Boundary

Local tests can cover timestamp assignment and merge decision behavior where practical. Additive Delta schema migration, CDF compatibility, and UTC session behavior require a Databricks runtime and remain subject to runtime verification when one is available.
