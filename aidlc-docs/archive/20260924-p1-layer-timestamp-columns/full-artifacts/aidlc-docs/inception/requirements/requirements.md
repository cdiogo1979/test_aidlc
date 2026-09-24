# P1 Layer Timestamp Columns — Requirements

## Intent Analysis

- **User request**: Add a timestamp column to the P1 bronze and silver tables.
- **Request type**: Enhancement to an existing Databricks workload.
- **Scope estimate**: Two existing notebooks and their Delta table creation/schema-evolution logic; the job definition and shared configuration remain unchanged.
- **Complexity estimate**: Moderate. The change adds distinct per-layer timestamps and must preserve semantics across Delta schema evolution, silver upserts, and stream retries.
- **Workspace context**: The previous intent did not run notebooks in Databricks. Tables are defined by code but have not been confirmed created in a live workspace.

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Preserve the existing Kafka event-time column `source_timestamp` in bronze and silver; the new columns represent processing/ingestion time, not source-event time. |
| FR-02 | Add `bronze_ingestion_timestamp TIMESTAMP` to the bronze table. Assign it when a Kafka source record is first inserted into bronze. |
| FR-03 | Add `silver_processing_timestamp TIMESTAMP` to the silver table. Assign it when a valid event is inserted into silver or when a newer event causes the current row for an `event_key` to be updated. |
| FR-04 | Use UTC instants for both new timestamp columns. Configure timestamp generation/session interpretation consistently with UTC. |
| FR-05 | Keep the bronze ingestion time and silver processing time distinct; do not copy one layer's timestamp into the other. |
| FR-06 | Preserve timestamp values on duplicate/replayed Kafka records that do not produce a new bronze insert or a winning silver insert/update. Retrying the same committed source event must not refresh its recorded layer timestamp. |
| FR-07 | When a target Delta table does not exist, create it with the new nullable timestamp column. When it already exists without the column, add the column using a safe additive schema migration before writes. |
| FR-08 | Leave the new column `NULL` for pre-existing rows when it is added to a table. Do not infer historical layer times from `source_timestamp` and do not assign migration time to old rows. |
| FR-09 | Keep current incremental processing, checkpoint paths, bronze CDF, silver latest-event ordering, and quarantine behavior unchanged. |

## Non-Functional Requirements

- **Data correctness**: Distinguish Kafka event time from each layer's processing time and retain the accepted value across retries.
- **Compatibility**: Schema migration must be additive and preserve existing columns, records, checkpoints, and table properties.
- **Timezone**: Use Spark/Delta `TIMESTAMP` values representing UTC instants.
- **Failure handling**: If an existing table cannot be safely migrated or validated, fail the notebook task with a clear error rather than silently writing inconsistent rows.
- **Performance**: No new numeric throughput or latency target is specified. Timestamp derivation must not introduce a separate action or scan per row beyond existing processing.
- **Security and extensions**: Security Baseline, Property-Based Testing, and Resiliency Baseline remain disabled, carried forward from the approved project baseline.

## Scenarios

1. A Kafka record is first inserted into bronze: it receives `bronze_ingestion_timestamp`; its Kafka `source_timestamp` remains unchanged.
2. Bronze processes the same Kafka identity again after a retry: the insert-only merge does not replace the original bronze timestamp.
3. A valid bronze event is the first or newer event for its `event_key`: silver writes `silver_processing_timestamp` for that silver insert/update.
4. The same event is replayed, or an older event loses the latest-event comparison: silver does not update the current row or refresh `silver_processing_timestamp`.
5. An existing bronze or silver table lacks its new column: the notebook additively adds a nullable column; historical rows remain `NULL`.
6. A new table is created: its schema includes the appropriate timestamp column from the beginning.
7. A malformed event is quarantined: existing quarantine `ingestion_timestamp` behavior remains unchanged; this request does not add a new column to quarantine.

## Acceptance Criteria

- Bronze schema and writes contain `bronze_ingestion_timestamp` of type `TIMESTAMP`.
- Silver schema and writes contain `silver_processing_timestamp` of type `TIMESTAMP`.
- Both timestamps represent UTC instants and remain distinct from Kafka `source_timestamp`.
- Timestamp values are set on successful first inserts or accepted silver latest-row updates, and are not refreshed by duplicate/no-op replay.
- Existing tables missing the column are additively migrated; existing records remain `NULL` in the new column.
- New table creation includes the column, while CDF, checkpoints, latest-event ordering, quarantine writes, and job dependencies remain unchanged.
- Local tests cover timestamp projection and merge decisions where practical. Databricks Delta migration/CDF behavior remains subject to runtime verification when an environment is available.

## Scope Exclusions and Limitations

- No `source_timestamp` behavior changes.
- No new timestamp column is added to quarantine; it already has `ingestion_timestamp`.
- No historical timestamp backfill is performed.
- No live Delta tables are migrated during this workflow because no Databricks environment is available.
- No Bundle/job schedule, security configuration, or deployment change is requested.
