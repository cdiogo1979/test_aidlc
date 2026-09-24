# U2 Silver Processing and Quarantine — Business Rules

1. **Input boundary**: Read source values and metadata from `test_prod.p1_test_kfk_brz`; U2 does not read Kafka directly.
2. **Payload interpretation**: Parse each non-null source value as JSON. Require a JSON object because event properties and `event_key` are read from object properties.
3. **Event key**: `event_key` must be a string with at least one non-whitespace character. Missing, null, blank, and non-string values are invalid. Do not coerce or normalize a valid key.
4. **Permissive property handling**: Do not require fields beyond `event_key` and do not reject events for property type mismatches. Preserve all other top-level properties, including unknown and nested properties, in the extensible `attributes` object. Absent properties are not synthesized. The approved physical representation is Delta `VARIANT`.
5. **Silver business identity**: The current-state key is `event_key`; silver contains no more than one current row for each key.
6. **Latest-event ordering**: Compare Kafka source timestamp first, then partition and offset for timestamp ties, following the approved requirements assumption. Apply the same ordering within a batch and against the current silver row.
7. **Silver idempotency**: Use `(topic, partition, offset)` to recognize reprocessed source records. A repeated event does not create another current row or replace a later-ranked event.
8. **Quarantine eligibility**: Invalid JSON, non-object JSON roots, and invalid `event_key` values are excluded from silver and written to quarantine.
9. **Quarantine contents**: Preserve raw payload, topic, partition, offset, source timestamp, ingestion timestamp, and a diagnostic describing parse or key-validation failure.
10. **Quarantine idempotency**: Deduplicate quarantine by `(topic, partition, offset)`. A retry does not create another logical quarantine record for the same source record.
11. **Record isolation**: A malformed event must not prevent other valid records in the same run from being made available in silver.
12. **Atomic outcome**: A read or output persistence failure makes the U2 task fail; it must not report successful completion for a partial result. Reprocessing is safe under the silver ordering and source-identity deduplication rules.
