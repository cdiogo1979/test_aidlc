# Integration Test Instructions: P1 Streaming Lookback

## Status and Environment

Integration testing was not performed. It requires a Databricks workspace with the P1 job, Kafka access, Delta CDF enabled on the bronze table, and permission to remove the two configured S3 checkpoint paths. No such test environment is available in this workflow session.

Run these scenarios only in an approved non-production environment with representative retained source history and isolated checkpoints:

1. **Default continuation:** run both job parameters at `0`; verify each notebook resumes from its existing checkpoint and emits its run summary.
2. **Bronze replay:** set `bronze_lookback_days` to a positive value and silver to `0`; verify only the bronze checkpoint resets and Kafka records at/after the UTC cutoff are merged without duplicate source identities.
3. **Silver replay:** set `silver_lookback_days` to a positive value and bronze to `0`; verify only the silver checkpoint resets and CDF changes at/after the cutoff update silver/quarantine idempotently.
4. **Coordinated replay:** set both values to the same positive day count; confirm the existing bronze-before-silver dependency and compare each layer's reported cutoff and first observed source timestamp.
5. **Input and history boundaries:** verify negative/non-integer values fail before checkpoint access, checkpoint removal failures stop query creation, and expired history behavior is reported accurately by the source.

After a successful replay, set that layer's parameter to `0` on the next run to continue from the advanced checkpoint. Positive values intentionally reset and repeat the replay. Do not use production data or checkpoints for these scenarios without separate approval.
