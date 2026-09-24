# U2 Silver Processing and Quarantine — Logical Components

## Component overview

| Component | Responsibility | Reliability / security boundary |
|---|---|---|
| U3 Databricks job | Runs U1 before U2 on the approved daily schedule and exposes task run status. | U2 starts only after U1 succeeds. Retry count and schedule timing are deployment settings. |
| U2 silver notebook | Reads the daily bronze increment, parses and classifies records, applies current-state ordering, and coordinates both output writes. | Fails the task on read or output persistence errors; logs operational status and safe counts/source identifiers only. |
| Bronze Delta table `test_prod.p1_test_kfk_brz` | Supplies raw payloads and Kafka source identity/metadata to U2 through Delta Change Data Feed. U1 enables CDF. | Access follows existing approved Databricks controls and table policies. CDF/table retention must cover the stream recovery window. |
| U2 Structured Streaming checkpoint | Stores the consumed bronze CDF progress across daily `AvailableNow` runs. | Stable path `{data_path}/checkpoints/P1/silver_processing`; accessible to the shared P1 job identity and retained across runs. |
| Silver Delta table `test_prod.p1_test` | Stores the current event per valid `event_key`, including extensible attributes and winning source metadata. | Idempotent by source identity; current state updates follow the approved event ordering. |
| Quarantine Delta table `test_prod.p1_test_kfk_quarantine` | Stores invalid source records, raw payload, source metadata, and parse/validation diagnostics. | Idempotent by source identity; access follows existing approved controls. Raw payload is kept out of task logs. |
| Environment configuration | Supplies environment-specific table/database/storage values as required by the existing P1 configuration contract. | Values vary by environment; secret material stays in the approved secret store. |

## Interaction and failure behavior

1. U3 starts U2 after U1 succeeds; U1 ensures CDF is enabled on bronze before ingesting.
2. U2 reads the bronze CDF using the stable stream checkpoint. A new stream processes the current bronze table snapshot as inserts before advancing to future changes.
3. U2 separates supported insert events into valid and quarantine candidates and writes outputs idempotently by `(topic, partition, offset)`.
4. If either write fails, the callback fails and the stream checkpoint does not commit that batch. A prior successful output may remain visible because the tables do not share an atomic transaction; replay safely repeats it.
5. A configured retry or later run resumes from the CDF checkpoint. Silver ordering prevents an older event from replacing a later current row.
6. If required CDF history has expired, the source fails rather than silently skipping changes. Recovery requires a deliberate full refresh/rebuild and checkpoint reset.
7. Databricks task status and concise logs provide the selected operational visibility. No separate monitoring, alerting, queue, cache, or retry-coordination component is added.

## Design boundaries

- This is a logical component view. Cluster/compute sizing, table physical layout, and deployment topology are handled in Infrastructure Design.
- It does not assert cross-table atomicity or platform-wide exactly-once behavior.
- Existing Databricks access controls and platform protections remain the security baseline; no new compliance component is introduced.
