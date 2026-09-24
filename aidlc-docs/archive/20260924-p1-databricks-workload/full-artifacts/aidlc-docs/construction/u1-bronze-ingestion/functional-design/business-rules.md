# U1 Bronze Ingestion — Business Rules

1. **Configured source**: Read only the configured Kafka topic `my-topic`, using the selected environment's Kafka hosts and secret reference. Secret material must not be embedded in repository artifacts.
2. **First-run position**: When no durable checkpoint exists, start at the earliest offset available from Kafka.
3. **Incremental position**: On later runs, continue from the durable checkpoint so successfully committed source progress is retained across daily runs.
4. **Source fidelity**: Preserve each Kafka value unchanged, together with the Kafka key, headers, topic, partition, offset, and source timestamp.
5. **Stable source identity**: The identity of a source record is `(topic, partition, offset)`. Reprocessing the same identity must not result in a duplicate bronze record.
6. **No payload validation in U1**: Do not parse, normalize, filter, or reject payloads based on JSON validity in Bronze. U2 validates payloads and quarantines malformed messages.
7. **Null values**: Kafka null-value/tombstone records are excluded from the expected topic contract. U1 does not define special tombstone handling.
8. **Failure handling**: Kafka read or bronze persistence failures fail the task; U1 does not intentionally skip failed input or advance successful progress past an uncommitted write. Retry and later-run behavior resumes from the last committed checkpoint.
9. **Checkpoint and identity complement each other**: The checkpoint tracks incremental progress; source identity protects the bronze result when an already-seen offset is presented again. This rule does not assert a platform-wide exactly-once guarantee.
10. **Downstream availability**: U2 consumes only records made available by successful bronze persistence. U3 schedules U2 after U1 succeeds.
11. **Downstream change feed**: Enable Delta Change Data Feed on the bronze table when created, and on an existing table before further ingestion, so U2 can consume the initial snapshot and subsequent changes incrementally. CDF/table history retention must allow the scheduled U2 stream to resume; do not silently skip missing change history.
