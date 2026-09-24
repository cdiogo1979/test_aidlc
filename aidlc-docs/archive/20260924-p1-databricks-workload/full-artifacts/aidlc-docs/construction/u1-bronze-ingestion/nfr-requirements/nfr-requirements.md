# U1 Bronze Ingestion — NFR Requirements

## Scope and source

These requirements apply to U1, which reads Kafka topic `my-topic` incrementally and persists source records and Kafka metadata to the bronze Delta table `test_prod.p1_test_kfk_brz`. They are based on the approved NFR questionnaire, P1 requirements, and approved U1 Functional Design.

## Requirements

| Area | Requirement | Target/status |
|---|---|---|
| Schedule | U1 participates in the once-daily P1 job. | Daily schedule is approved; exact execution time/time zone are deployment details. |
| Performance and scale | Process the available incremental Kafka data for the daily run. | Expected daily volume, growth rate, and maximum completion window are unspecified; no numeric throughput or latency SLA is approved. |
| Reliability | Retain incremental progress across successful runs. A Kafka read or bronze persistence failure fails the task; retry or a later run resumes from the last committed checkpoint. | Required behavior, defined in FR-03 and U1 Functional Design. No bounded recovery-time target is specified. |
| Availability | Failed runs must be visible as failed Databricks task/job runs. | No uptime target, failover target, or missed-run recovery deadline is specified. |
| Data integrity | Preserve source values and the selected Kafka metadata. Replayed `(topic, partition, offset)` identities must not create duplicate logical bronze records. | Required behavior in U1 Functional Design. No broader exactly-once guarantee is claimed. |
| Security | Retrieve Kafka credentials through the configured Databricks secret reference. Do not place secret values in repository files, notebook source, or job/bundle configuration. | Required by FR-02. Use existing approved Databricks access controls; no additional classification, compliance, or encryption policy was specified in this assessment. |
| Observability | Databricks job/task run status and task logs provide the required initial operational visibility. | No additional alerts, recipients, custom metrics, or thresholds are specified. |
| Retention and recovery horizon | Preserve bronze records and checkpoint state according to the applicable platform/table policies. | No retention period, Kafka replay horizon, or checkpoint cleanup policy is specified by this assessment. These policies must not undermine the ability to resume from committed progress. |
| Maintainability | Keep environment-specific connection values in `configs/{environment}.yaml` and use the repository's P1 notebook/job layout. | Required by repository conventions and approved design. |

## Explicitly unspecified targets

The following remain open operational targets rather than implicit promises: daily record count and growth, processing completion deadline, uptime/recovery-time objective, bronze/checkpoint retention duration, and alert thresholds. Set these when workload volume and operating policies are known.

## Traceability

- **FR-02**: Configured Kafka connection and secret reference; no checked-in secret material.
- **FR-03**: Once-daily incremental processing with durable progress.
- **FR-04**: Source preservation and metadata traceability in bronze.
- **U1 Functional Design**: Earliest available offsets on an uncheckpointed first run; resume from committed progress; task failure on read/write errors; deduplicate using source identity.
- **User NFR answers**: Questions 1–5 all selected option A; no numeric performance, recovery, or retention targets or additional controls were provided.
