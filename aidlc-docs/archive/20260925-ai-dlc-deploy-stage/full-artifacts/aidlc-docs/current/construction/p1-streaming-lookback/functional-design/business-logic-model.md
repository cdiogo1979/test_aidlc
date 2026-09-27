# Business Logic Model: P1 Streaming Lookback

## Purpose

Allow an operator to either continue a P1 layer from its current Structured Streaming checkpoint or deliberately replay that layer from a source-time lookback point.

## Actors and Components

- **Operator**: Sets `lookback_days` independently for bronze and silver task runs.
- **P1 daily job**: Executes the bronze task before the dependent silver task and provides each task's parameter.
- **Bronze ingestion**: Reads Kafka and merges unseen `(topic, partition, offset)` records into bronze.
- **Silver processing**: Reads bronze Delta Change Data Feed (CDF), merges the latest valid event by `event_key`, and inserts malformed records into quarantine by Kafka identity.

## Processing Flow

### Normal continuation (`lookback_days = 0`)

1. Parse and validate the widget value before touching checkpoint storage.
2. Validate configuration and layer prerequisites.
3. Keep the existing checkpoint unchanged.
4. Start `AvailableNow` without a source start-time override. Existing checkpoints determine the resume position. On a first-ever query, retain the current source's initial behavior.
5. Persist through the existing idempotent merge operations.

### Replay (`lookback_days > 0`)

1. Parse a non-negative integer and calculate one UTC cutoff from the task's run-start time minus the requested number of days.
2. Validate locally checkable configuration, secrets/source options, destination tables, and source metadata prerequisites before checkpoint removal. Actual Kafka or Delta source connectivity is established only when the stream starts.
3. Find the exact checkpoint directory under the configured checkpoint parent. Recursively remove only that layer's checkpoint; if removal fails, stop before creating the query.
4. Start a new query with the source-specific cutoff:
   - **Bronze**: Kafka `startingTimestamp` in epoch milliseconds, resolved against Kafka record timestamps.
   - **Silver**: Delta CDF `startingTimestamp` in UTC timestamp form, resolved against bronze CDF commit timestamps.
5. If requested history predates retained history, read from the earliest history the source can still return. Record the requested cutoff and the first observed source timestamp/commit timestamp to make the shorter effective window visible.
6. Persist through the existing idempotent merge operations and the layer's existing checkpoint location. Subsequent runs with `0` resume from the replay's advanced checkpoint.

## End-to-End Coordination

The bronze and silver parameters are independent. To replay both layers from a matching lookback window, set the same positive day count for both tasks and run the existing dependency order (bronze then silver). A single-layer replay may use a positive value for one task and `0` for the other, subject to normal job dependency behavior.

## Data Flow

```text
lookback_days = 0
  -> preserve checkpoint -> resume source -> existing merge writes

lookback_days > 0
  -> validate inputs/prerequisites -> calculate UTC cutoff -> remove layer checkpoint
  -> start source at cutoff -> report requested/effective source time -> idempotent writes
  -> checkpoint advances -> later zero-day run resumes
```

## Failure Outcomes

- Invalid, blank, or negative values fail before checkpoint storage is touched.
- Missing configuration, locally detectable source/table prerequisites, or failed checkpoint removal fail the task before a replay query starts. Connectivity failures can occur after the checkpoint has been reset, when the replay query starts.
- Source/table/write failures propagate through the task; the existing `AvailableNow` query does not report success unless it terminates successfully.
- A partially completed replay may have written some output before failure. Existing merges make a retry safe for the same source identities; positive lookback retries reset and replay again.
- A positive lookback can read a large retained range and increase runtime and compute cost. No production run is implied or authorized by this design.
