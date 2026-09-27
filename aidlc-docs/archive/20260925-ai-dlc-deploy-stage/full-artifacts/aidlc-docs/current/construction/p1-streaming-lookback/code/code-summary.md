# Code Summary: P1 Streaming Lookback

## Modified Files

- `notebooks/P1/bronze/bronze_ingestion.py`
  - Added the `bronze_lookback_days` widget, displayed as **Lookback days**, with default `0` and non-negative integer validation.
  - Positive values compute a UTC cutoff, remove only the bronze checkpoint, start Kafka from the requested timestamp, and filter records against the cutoff.
  - Tracks the earliest observed Kafka record timestamp across micro-batches and emits a JSON run summary, including whether the observed window starts after the requested cutoff, to task logs.
  - Zero preserves checkpoint continuation and the existing initial-source behavior.
- `notebooks/P1/silver/silver_processing.py`
  - Added the `silver_lookback_days` widget, displayed as **Lookback days**, with default `0` and non-negative integer validation.
  - Positive values compute a UTC cutoff, remove only the silver checkpoint, and start CDF processing from the requested commit timestamp.
  - Tracks the earliest observed CDF commit timestamp across micro-batches and emits a JSON run summary, including whether the observed window starts after the requested cutoff, to task logs.
  - Zero preserves checkpoint continuation and existing CDF behavior.
- `jobs/P1/resources/p1-daily-pipeline.yml`
  - Added independent job-level `bronze_lookback_days` and `silver_lookback_days` parameters, each defaulting to string value `"0"`; retained the shared `environment` job parameter and task dependency.

## Replay Safety

Both notebooks validate parameters and locally checkable source/table prerequisites before removing checkpoints. Source connectivity is only established when the query starts, so a connectivity failure can happen after reset. Checkpoint removal is limited to the exact layer path and fails before stream start if removal fails. Existing bronze, silver, and quarantine merge identities are unchanged. Positive values intentionally reset the layer checkpoint each time; subsequent normal runs use zero to resume the new checkpoint. The per-batch timestamp aggregation adds compute overhead.

## Verification Status

No automated tests, notebook runs, Kafka reads, Delta operations, S3 checkpoint operations, Bundle deployment, or production operations were performed. Databricks runtime behavior remains unverified because no Databricks environment is available.
