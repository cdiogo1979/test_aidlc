# U1 Bronze Ingestion — NFR Requirements Plan

## Unit context

- **Unit**: U1 — Bronze Ingestion.
- **Functional design**: Approved. U1 reads Kafka incrementally, starts from the earliest available offset when no checkpoint exists, preserves source records in bronze, and fails on Kafka or write errors so a retry/later run can resume from committed progress.
- **Relevant requirements**: FR-02 (Kafka access and secret reference), FR-03 (daily incremental processing), FR-04 (bronze persistence), reliability, security, and data traceability.
- **Current known constraints**: Databricks workload; Delta bronze destination; `configs/{environment}.yaml`; secret values are held outside repository files; no numeric volume, latency, or processing-window target is currently approved.
- **Scope**: Identify measurable or explicit non-functional requirements and record technology decisions/constraints for U1. This plan does not design infrastructure or implement code.

## NFR assessment checklist

- [x] Confirm performance, daily volume, and processing-window targets or record that none are set.
- [x] Confirm availability and recovery expectations beyond the approved checkpoint/resume behavior.
- [x] Confirm security and access constraints for Kafka credentials, source data, and bronze records.
- [x] Confirm required operational visibility, failure notification, and audit needs.
- [x] Confirm retention or replay horizon requirements for source records and checkpoint data.
- [x] Record existing technology constraints and avoid re-opening approved Databricks/Kafka/Delta choices.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/nfr-requirements/nfr-requirements.md`.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/nfr-requirements/tech-stack-decisions.md`.
- [x] Validate consistency with approved requirements and U1 Functional Design.

## Question 1 — Throughput and completion window

What workload size and daily completion window must U1 support?

A) No numeric volume or completion-window target is set yet; retain the daily schedule and document the target as unknown.

B) Provide an expected daily record volume and maximum completion window after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Availability and recovery

What recovery expectation should apply if the daily U1 task fails?

A) Existing behavior is sufficient: fail visibly, use configured job retry or the next scheduled run, and resume from the last committed checkpoint; no uptime or recovery-time target is set.

B) A bounded recovery-time or missed-run recovery target is required; specify it after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 3 — Data access and protection

Which additional access or data-protection requirement applies to Kafka credentials and the bronze records?

A) Use existing approved Databricks access controls and secret storage; do not commit secret values. No additional classification, encryption, or compliance constraint has been specified.

B) Additional requirements apply; specify controls or applicable policy after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 4 — Monitoring and failure notification

What operational visibility is required for U1?

A) Databricks job run status and task logs are sufficient; no additional alerting or metric thresholds are required yet.

B) Require explicit alerting and/or metrics; specify the events, recipients/channel, and thresholds after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 5 — Data and checkpoint retention

What retention requirement applies to bronze source records and the incremental checkpoint?

A) No retention period is currently specified; retain according to existing platform/table and checkpoint policies until one is approved.

B) Specify a retention period and any replay/recovery horizon after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Fixed technology constraints

Databricks, Kafka, the Delta bronze destination, and environment configuration/secret references are established by approved requirements and design. Questions are limited to NFR targets and controls; this stage does not reopen these technology choices.
