# P1 Streaming Lookback

## Problem

Operators cannot select a historical replay window for the P1 Kafka-to-bronze and bronze-CDF-to-silver streaming tasks. Existing checkpoints otherwise resume from their last processed positions.

## Solution

Add independent day-based lookback parameters for bronze and silver. A value of `0` preserves normal checkpoint continuation. A positive value removes that layer's checkpoint and starts a new stream from the requested UTC cutoff, using Kafka record timestamps for bronze and Delta CDF commit timestamps for silver. Existing idempotent merge keys and bronze-before-silver task dependency remain in place.

## Main Changes

- `notebooks/P1/bronze/bronze_ingestion.py`: added `bronze_lookback_days`, cutoff filtering, isolated bronze checkpoint reset, and a task-log replay summary.
- `notebooks/P1/silver/silver_processing.py`: added `silver_lookback_days`, CDF cutoff handling, isolated silver checkpoint reset, and a task-log replay summary.
- `jobs/P1/resources/p1-daily-pipeline.yml`: added independent job parameters, each defaulting to `"0"`.
- `aidlc-docs/current/construction/p1-streaming-lookback/`: records approved requirements, design, NFRs, and implementation details.

## Verification

Static consistency review and targeted whitespace checks completed. No automated tests were added or run, and Bundle validation was not run because the Databricks CLI is unavailable in the current environment. No notebook execution, Kafka/Delta access, or S3 checkpoint operations were performed.

The user approved Build and Test with `**Approve & Continue**`, accepting the documented verification limitation. Databricks runtime behavior remains **unverified**; the waiver is not a pass, release approval, or production-readiness claim.

## Deployment

Ordered deployment and operational steps are required; see [deploy_instructions.md](deploy_instructions.md). The Bundle declares a `prod` production-mode target and the job schedule is `UNPAUSED`. Deployment is conditional on an explicit production deployment/schedule decision, required permissions and variables, and successful Bundle validation in the target workspace. Positive lookback runs are separate operational actions because they reset checkpoints.

## Risks and Limitations

- A positive lookback recursively removes the selected layer's checkpoint. Checkpoint state cannot be restored by this change; a failed replay may have partially written idempotent table updates.
- Kafka and Delta CDF history retention can shorten the replay window. Task logs report the requested cutoff and earliest observed source timestamp, but a later first timestamp can also reflect a quiet source period.
- The lookback summary adds an aggregation action per micro-batch and associated compute overhead.
- The deployed job remains scheduled when `UNPAUSED`; confirm whether creating/updating that schedule is approved before deployment.
- No non-production Databricks environment or rollback procedure for checkpoint state was provided. Complete the required validation in an approved environment before any production replay.
