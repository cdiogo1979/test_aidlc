# Integration Test Instructions — U4 P1 Layer Timestamp Metadata

## Status

Integration testing was not run because no Databricks environment is available. Perform these checks later in an isolated non-production workspace before deploying the change.

## Preconditions

- An isolated catalog/schema and Delta storage location with no production data.
- A supported P1 Databricks runtime, including existing `VARIANT` support.
- A test Kafka topic with controlled records and existing secret/configuration access.
- A test-specific checkpoint location so the production checkpoint is not reused or modified.
- Baseline copies or schema snapshots for bronze, silver, and quarantine tables.

## Scenario 1: Existing Tables Need Additive Migration

1. Prepare existing bronze and silver test tables without the new timestamp columns and with historical rows.
2. Run the updated bronze task and confirm the bronze column is nullable `TIMESTAMP`; confirm historical values are NULL.
3. Run the updated silver task and confirm the silver column is nullable `TIMESTAMP`; confirm historical values are NULL.
4. Confirm no old columns, rows, CDF properties, or checkpoint settings were changed.

## Scenario 2: Bronze First Insert and Replay

1. Publish a test Kafka record and run the bronze task.
2. Confirm the inserted row has a UTC `bronze_ingestion_timestamp` distinct in meaning from `source_timestamp`.
3. Replay the same Kafka identity through the test setup without changing production checkpoints.
4. Confirm the existing bronze timestamp is unchanged and no duplicate identity was added.

## Scenario 3: Silver Insert, Winning Update, and No-Op Replay

1. Process a valid event for a new `event_key`; confirm silver receives `silver_processing_timestamp`.
2. Process a newer event for that key; confirm silver updates to the newer event and records a new processing timestamp.
3. Replay the accepted event and process an older losing event; confirm neither changes the current row timestamp.
4. Confirm silver processing time was generated independently and was not copied from bronze ingestion time.

## Scenario 4: CDF and Quarantine Regression

1. Confirm newly inserted bronze records continue to appear in CDF after schema migration.
2. Process a malformed test event and confirm the existing quarantine schema and `ingestion_timestamp` behavior remain unchanged.
3. Confirm the daily job still runs bronze before silver with its current task parameters.

## Expected Results and Cleanup

- All scenarios meet the approved requirements and NFRs.
- Record Databricks Runtime version, test catalog, and evidence in the Build and Test summary.
- Remove only isolated test data and checkpoints after preserving the results. Do not run these scenarios against production tables or checkpoints.
