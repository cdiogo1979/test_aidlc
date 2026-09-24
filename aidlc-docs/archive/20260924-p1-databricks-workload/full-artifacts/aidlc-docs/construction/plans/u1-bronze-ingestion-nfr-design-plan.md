# U1 Bronze Ingestion — NFR Design Plan

## Unit context

- **Unit**: U1 — Bronze Ingestion.
- **Approved NFRs**: Daily incremental ingestion; resume from the last committed checkpoint after failure; preserve source identity; protect secret values; Databricks run status and logs are sufficient initial observability; no volume, latency, recovery-time, retention, or alert thresholds are set.
- **Technology constraints**: Databricks, Kafka, Structured Streaming with checkpointing, Delta bronze table, Python Databricks notebook, environment YAML, and Databricks secret reference.
- **Design boundary**: Select logical NFR patterns for U1. Runtime sizing, checkpoint URI, retry counts, and deployment permissions remain deployment/infrastructure details unless the user specifies otherwise.

## NFR design checklist

- [x] Define task retry and checkpoint recovery pattern.
- [x] Define scaling and compute policy given unknown workload size.
- [x] Define performance approach without inventing numeric targets.
- [x] Define security pattern for secret access and source/bronze access.
- [x] Define required logical components and observability integration.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/nfr-design/nfr-design-patterns.md`.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/nfr-design/logical-components.md`.
- [x] Validate patterns against the approved NFR Requirements and U1 Functional Design.

## Question 1 — Resilience and retries

How should U1 handle transient Kafka or Delta write failures?

A) Rely on the Databricks job's configured retry behavior and the durable checkpoint; do not add notebook-level retries or skip failed input. Define retry count/backoff with deployment settings.

B) Add explicit bounded retry/backoff inside the notebook; specify limits and delay after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Scalability and compute

How should compute scale while expected volume and growth remain unknown?

A) Use the deployment's approved Databricks compute policy for the daily task; add no workload-specific autoscaling target until volume is known.

B) Require a fixed compute profile or autoscaling bounds; specify the constraint after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 3 — Performance approach

Which performance design should U1 use without an approved latency or throughput target?

A) Use the standard incremental Structured Streaming path and preserve source records; defer workload-specific tuning until representative volume and measurements are available.

B) Require a specific throughput/completion objective or optimization approach; specify it after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 4 — Security pattern

How should U1 apply security controls given that no additional classification or compliance policy was specified?

A) Use existing approved Databricks access controls and the configured secret reference; grant the job access through deployment configuration and do not expose secret values in logs or artifacts.

B) Add specific access, encryption, or compliance controls; specify the policy and required behavior after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 5 — Logical components

Which logical components should U1 use for progress, persistence, and operational visibility?

A) Use the durable streaming checkpoint, bronze Delta table, Databricks task status/logs, and existing job retry mechanism; add no queue, cache, circuit breaker, or separate monitoring service.

B) Add a component or integration beyond those listed; specify its purpose and expected behavior after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A
