# U4 Logical Components — P1 Layer Timestamp Metadata

## Component Responsibilities

| Existing component | NFR design responsibility | Change boundary |
|---|---|---|
| Bronze ingestion notebook | Set UTC session interpretation; ensure and validate the nullable bronze timestamp column; attach a native Spark processing timestamp to candidate rows; retain insert-only merge and CDF properties. | Existing U1 notebook only. |
| Silver processing notebook | Set UTC session interpretation; ensure and validate the nullable silver timestamp column; attach a native Spark processing timestamp to accepted candidates; retain the existing latest-event predicate, CDF source, and quarantine path. | Existing U2 notebook only. |
| Bronze Delta table | Store the independent first-accepted bronze timestamp; expose the additive schema to downstream CDF consumers. | Existing table; additive nullable column only. |
| Silver Delta table | Store the independent silver current-state acceptance timestamp; leave historical migrated rows NULL. | Existing table; additive nullable column only. |
| Existing P1 Bundle job | Continue running bronze before silver with current parameters and schedule. | No change. |
| Local test suite | Exercise deterministic timestamp-field projection and merge decision logic where possible. | Tests added or adjusted during Code Generation. |

## Initialization and Write Boundaries

- Table creation/migration and schema validation happen before starting each notebook's stream.
- Bronze schema setup precedes bronze streaming writes; silver schema setup precedes CDF processing and silver writes.
- Migration failure stops that task before batch data writes. Existing task and stream failure propagation remains responsible for surfacing the error.
- Processing timestamps are evaluated in Spark and committed atomically with accepted Delta row changes.

## Explicitly Absent Components

No new library, service, queue, cache, migration job, backfill process, table, checkpoint, or orchestration task is introduced. No production Databricks environment is available for validating the live schema/CDF path as part of this design stage.
