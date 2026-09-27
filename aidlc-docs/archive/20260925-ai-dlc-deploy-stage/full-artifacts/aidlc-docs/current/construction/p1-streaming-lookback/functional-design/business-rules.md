# Business Rules: P1 Streaming Lookback

1. Each notebook has its own integer widget displayed as `Lookback days`, with default `0`. The bronze key is `bronze_lookback_days`; the silver key is `silver_lookback_days`.
2. Values must parse as integers and be greater than or equal to zero. Validation occurs before any checkpoint operation.
3. A zero value does not remove or replace the existing checkpoint and does not add a starting timestamp to the source query.
4. A positive value requests a replay from `UTC task start time - lookback_days` and resets only the checkpoint owned by that notebook.
5. Bronze interprets the cutoff using Kafka record timestamps. Silver interprets it using Delta CDF commit timestamps.
6. All prerequisites that can be checked without starting a stream are validated before removing the checkpoint.
7. Checkpoint removal is recursive and limited to the exact configured layer checkpoint path. If an existing checkpoint cannot be removed, the task fails before starting a source query.
8. When the requested cutoff predates retained source history, the source's earliest available history is processed; logs identify the requested cutoff and the first observed source timestamp or CDF commit timestamp. If no records are returned, logs state that no effective source timestamp was observed.
9. Bronze uniqueness remains `(topic, partition, offset)`. Replay must not add a duplicate row for an already persisted Kafka identity.
10. Silver state remains the latest valid event per `event_key`, ordered by source timestamp, partition, and offset. Replayed older input does not replace newer state.
11. Quarantine uniqueness remains `(topic, partition, offset)`; replay does not duplicate an already quarantined source identity.
12. Bronze and silver lookback values are independent. Matching values are required only when an operator intends to replay both layers from a matching lookback window.
13. With a positive lookback, any later normal run must use `0` to resume the checkpoint created by the replay. Reusing a positive value intentionally resets and repeats the replay.
14. Environment names and secrets remain governed by existing configuration and Databricks Secrets behavior; no credentials are added to widgets or job parameters.
