# U4 Business Rules — P1 Layer Timestamp Metadata

| ID | Rule |
|---|---|
| BR-01 | `source_timestamp` remains Kafka event time; it is not repurposed or overwritten. |
| BR-02 | Bronze assigns `bronze_ingestion_timestamp` to a record when its Kafka identity is first inserted into bronze. |
| BR-03 | A duplicate bronze identity must not update the existing row or refresh its ingestion timestamp. |
| BR-04 | Silver assigns `silver_processing_timestamp` when a valid event is inserted as current state or wins the existing latest-event comparison and updates current state. |
| BR-05 | A silver candidate that does not insert or win the existing latest-event comparison must not change the current row or its processing timestamp. |
| BR-06 | Bronze and silver timestamps are distinct UTC instants. Silver must not copy `bronze_ingestion_timestamp` into its timestamp field. |
| BR-07 | A newly created table includes the corresponding nullable timestamp column. |
| BR-08 | An existing table missing the column receives an additive nullable `TIMESTAMP` column before data writes. Existing rows remain `NULL`; no historical value is inferred or backfilled. |
| BR-09 | If the expected column exists with an incompatible type, or additive migration/validation fails, fail clearly before processing writes. |
| BR-10 | Existing Kafka identity, silver winner ordering, checkpoint, CDF, quarantine, and job behavior remain unchanged. |
| BR-11 | A processing instant is persisted only for a merge-accepted insert/update. A failed uncommitted attempt may be retried with a later instant; a committed row's timestamp is stable under replay. |
| BR-12 | Malformed events continue through the existing quarantine path; this change does not add fields to quarantine or alter its `ingestion_timestamp`. |

## Invariants

- Both new fields use the timestamp type representing UTC instants.
- Previously accepted rows are never assigned a new layer timestamp by a duplicate or no-op replay.
- Silver current-state ordering continues to use the existing source timestamp, partition, and offset rules, never either processing timestamp.
