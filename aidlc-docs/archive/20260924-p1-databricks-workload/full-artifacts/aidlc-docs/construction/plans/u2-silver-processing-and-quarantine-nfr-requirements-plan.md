# U2 Silver Processing and Quarantine — NFR Requirements Plan

## Unit context

- **Unit**: U2 — Silver Processing and Quarantine.
- **Functional design**: Approved. U2 reads bronze records, parses JSON with permissive property handling, stores `event_key` plus an extensible attributes map in silver, and quarantines invalid JSON roots/keys. Silver and quarantine are idempotent by `(topic, partition, offset)`.
- **Outputs**: Silver Delta table `test_prod.p1_test`; quarantine Delta table `test_prod.p1_test_kfk_quarantine`.
- **Relevant requirements**: FR-05, FR-06, FR-07, FR-08; data integrity, reliability, security, and operational visibility.
- **Known workload constraints**: Part of the once-daily Databricks job. U1 has no approved numeric volume, completion-window, uptime, recovery-time, monitoring threshold, or retention target; determine whether U2 has additional requirements.
- **Fixed technology constraints**: Databricks notebooks and Delta tables are established. Configuration remains in `configs/{environment}.yaml`; secret values remain outside repository artifacts. This stage does not reopen those choices or design infrastructure.

## NFR assessment checklist

- [x] Confirm daily input volume, growth, and completion-window targets or record that none are set.
- [x] Confirm availability and recovery expectations for U2 and partial silver/quarantine writes.
- [x] Confirm data access, protection, and compliance constraints for silver and quarantine.
- [x] Confirm operational visibility, failure notification, and audit needs.
- [x] Confirm silver and quarantine retention/replay requirements.
- [x] Record fixed technology choices and any implementation constraints.
- [x] Generate U2 `nfr-requirements.md` and `tech-stack-decisions.md`.
- [x] Validate consistency with approved requirements and U2 Functional Design.

## Answers applied

Questions 1, 2, 4, 5, and 6 selected A. Question 3 selected A: fail U2 if either silver or quarantine persistence fails and retry/replay using idempotent writes. No numeric service targets or additional controls were specified.

## Question 1 — Throughput and completion window

What daily volume and completion window must U2 support?

A) No numeric volume, growth, or completion-window target is set yet; process the daily bronze increment and record targets as unknown.

B) Provide expected daily records/bytes, growth, and maximum completion window after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Availability and recovery

What recovery expectation should apply if U2 fails during the daily run?

A) Fail the task visibly; configured retry or a later run reprocesses bronze records, relying on source-identity idempotency and latest-event ordering. No bounded recovery-time or uptime target is set.

B) Require a bounded recovery-time, missed-run, or availability target; specify it after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 3 — Partial silver and quarantine writes

If one output has been persisted but writing the other output fails, how should the run behave?

A) Fail the U2 task and retry the input; idempotent silver/quarantine writes reconcile the replay (Recommended).

B) Continue and report success when either output fails; record the failure for later reconciliation.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 4 — Data access and protection

Which additional access, protection, or compliance requirements apply to silver and quarantine data?

A) Use existing approved Databricks access controls and platform protections; no additional classification, encryption, or compliance constraint is specified.

B) Additional requirements apply; specify controls or applicable policy after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 5 — Monitoring and failure notification

What operational visibility is required for U2?

A) Databricks job/task status and logs are sufficient; no additional alerts, recipients, custom metrics, or thresholds are required yet.

B) Require specific alerts or metrics; provide events, recipients/channel, and thresholds after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 6 — Silver and quarantine retention

What retention and replay horizon should apply to the current-state silver and quarantine records?

A) No U2-specific retention period is set; follow existing platform/table policies and do not remove data in a way that defeats required current-state use or replay support.

B) Specify retention periods and any replay/recovery horizon after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Fixed technology constraints

Databricks notebooks, Delta tables, the configured environment file, and the established P1 folder layout are fixed by the approved design and repository. Questions focus on NFR targets and controls, not infrastructure topology or code-level implementation.
