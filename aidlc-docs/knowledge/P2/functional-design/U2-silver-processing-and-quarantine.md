# U2 P2 Silver Processing and Quarantine — Functional Design

## Purpose and boundary

Read P2 bronze Delta snapshot/CDF, validate and shape JSON events, maintain P2 current state, and quarantine invalid records. U2 does not read or write P1 tables or checkpoints.

## Inputs and outputs

- **Input**: `<database>.p2_test_kfk_brz` and its Delta CDF.
- **Configuration**: Shared `configs/prod.yaml` and `silver_lookback_days` parameter.
- **Outputs**: `<database>.p2_test` and `<database>.p2_test_kfk_quarantine`.
- **Progress**: `{data_path}/checkpoints/P2/silver_processing`.

## Business logic and rules

1. Consume the P2 bronze initial snapshot and changes through CDF, retaining P1's validation and event-ordering behavior.
2. Accept valid object JSON with a nonblank string `event_key`; preserve extensible attributes and retain the latest event per key under P1's source timestamp, partition, and offset order.
3. Route invalid JSON or invalid event keys to P2 quarantine with raw payload, source identity/time, and diagnostic context.
4. With zero lookback, continue from the P2 silver checkpoint. Positive lookback resets/replays only P2 silver processing according to the P1 contract.
5. Preserve P1's processing timestamp and additive nullable schema behavior while using P2-owned tables/checkpoints.

## Failure and recovery

Missing or unavailable CDF history, table/schema errors, or read/write failures fail the task rather than silently skipping changes. Retries resume using P2 checkpoint state and idempotent merge behavior.
