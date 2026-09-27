# NFR Requirements Plan: P1 Streaming Lookback

## Unit

`p1-streaming-lookback`

## Assessment Steps

- [x] Review the approved functional design and existing P1 workload constraints.
- [x] Confirm the maximum permitted lookback or retention-based limit — no configured cap; source retention bounds replay.
- [x] Confirm replay throughput/throttling expectations for Kafka and CDF — keep existing `AvailableNow` behavior without new per-trigger limits.
- [x] Confirm operator-visible replay status and monitoring expectations — emit the requested and observed window to task logs only.
- [x] Document availability, recovery, security, maintainability, and runtime constraints.
- [x] Confirm whether the existing Databricks/Kafka/Delta stack remains sufficient — no new technology.
- [x] Record NFR requirements and technology decisions.

## Questions

The following decisions affect replay guardrails and operational cost. The available workflow question tool is not present, so answers are collected in the linked file using `[Answer]:` tags.

- `aidlc-docs/current/construction/plans/p1-streaming-lookback-nfr-requirements-questions.md`

## Intended Artifacts

- `aidlc-docs/current/construction/p1-streaming-lookback/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/current/construction/p1-streaming-lookback/nfr-requirements/tech-stack-decisions.md`

## Review Status

NFR Requirements were approved by the user with “Continue to Next Stage” on 2026-09-25. Code Generation Part 1 was approved with “pprove & Continue” on 2026-09-25; Part 2 generation is complete and under static review.
