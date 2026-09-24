# U2 Silver Processing and Quarantine — NFR Requirements

## Scope and source

These requirements apply to U2, which reads bronze Delta records and writes the silver current-state table `test_prod.p1_test` and quarantine table `test_prod.p1_test_kfk_quarantine`. They are based on the approved U2 Functional Design and NFR answers. U2 runs as part of the once-daily P1 Databricks job after U1 succeeds.

## Requirements

| Area | Requirement | Target/status |
|---|---|---|
| Schedule | U2 participates in the once-daily P1 job after successful U1 completion. | Daily schedule is approved; exact execution time and time zone are deployment details. |
| Performance and scale | Process the available daily bronze increment. | Expected volume, growth, and maximum completion window are unspecified; no numeric throughput or latency SLA is approved. |
| Reliability and recovery | Read the bronze Delta Change Data Feed with a stable Structured Streaming checkpoint. Fail the Databricks task visibly on source, output, or CDF history errors. Configured retry or a later run may reprocess records safely using source-identity idempotency and latest-event ordering. | No uptime, bounded recovery-time, or missed-run recovery target is specified. Checkpoint must persist across daily runs; CDF/table retention must cover the scheduled stream's recovery window. |
| Partial output failure | If silver or quarantine persistence fails after the other output was written, fail the task. Retry/replay must reconcile both outputs through their idempotent source identity handling. | Required by approved NFR answer; no cross-table transaction guarantee is claimed. |
| Data integrity | Keep one current silver row per `event_key`; apply the approved source timestamp, partition, and offset ordering. Deduplicate silver and quarantine processing by `(topic, partition, offset)`. | Required by U2 Functional Design. No broader exactly-once guarantee is claimed. |
| Security and access | Use existing approved Databricks access controls and platform protections for bronze, silver, and quarantine. Keep secrets out of source and configuration artifacts. | No additional data classification, encryption, or compliance requirement was specified. |
| Observability | Databricks job/task status and task logs provide initial operational visibility for U2. | No additional alerts, recipients, custom metrics, or thresholds are specified. |
| Retention and replay horizon | Follow existing platform/table retention policies for silver and quarantine. Policies must not remove current state needed by consumers or data needed for the supported replay/recovery process. | No U2-specific retention duration or replay horizon is specified. |
| Maintainability | Keep U2 in the P1 silver notebook location, follow the repository notebook structure and docstring conventions, and use existing environment configuration practices. | Required by approved repository conventions and design. |

## Explicitly unspecified targets

Daily input volume and growth, completion deadline, uptime and recovery-time objectives, custom alert thresholds, and table retention/replay durations remain unspecified. Establish these when operating volumes and platform policies are known.

## Traceability

- **FR-05 / FR-06 / FR-07**: Parse event payloads, maintain latest current state, and quarantine malformed messages.
- **FR-08**: Use the selected environment configuration.
- **U2 Functional Design**: Process valid and malformed records independently; use source identity for idempotency; fail the task when persistence fails.
- **CDF processing**: CDF is enabled on bronze by U1. The U2 streaming checkpoint tracks consumed table versions; if retained change history is unavailable, fail visibly and require a deliberate downstream refresh rather than ignoring data loss.
- **User NFR answers**: Questions 1–6 selected option A, except Question 3 selected option A for failing on partial silver/quarantine output failure and retrying idempotently. No numeric performance, recovery, monitoring, security, retention, or replay targets were added.
