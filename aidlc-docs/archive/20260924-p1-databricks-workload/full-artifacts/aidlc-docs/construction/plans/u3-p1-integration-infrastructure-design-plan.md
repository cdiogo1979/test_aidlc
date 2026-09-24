# U3 P1 Integration — Infrastructure Design Plan

## Unit context

- **Unit**: U3 — P1 Integration.
- **Workload**: One daily Databricks job running the U1 bronze notebook followed by the U2 silver/quarantine notebook.
- **Approved logical constraints**: One active run maximum; job-native queueing enabled; U2 depends on U1 success; both tasks receive the same environment value; task failures fail the job; U1/U2 checkpoints are retained.
- **Shared platform decisions inherited from U1/U2**: Existing P1 Databricks workspace/environment, approved Databricks job compute policy, `test_prod` catalog/database and `s3://test_prod` storage conventions, shared P1 job identity and approved grants, existing Databricks-to-Kafka route owned by U1, and Databricks job/task status and logs.
- **Scope boundary**: U3 owns the Databricks job definition under `jobs/P1/` (Declarative Automation Bundle YAML selected during Code Generation clarification), its daily schedule, task parameters/dependency, concurrency, queueing, job-level retries, and optional native job notifications. U1 owns Kafka connectivity/checkpoint; U2 owns silver/quarantine resources and CDF checkpoint. U3 introduces no new storage, broker, network, monitoring service, or compute resource.

## Infrastructure assessment checklist

- [x] Review U3 Functional Design, NFR Requirements, NFR Design, and U1/U2 infrastructure decisions.
- [x] Map deployment environment, compute, storage, messaging, networking, observability, and shared infrastructure; applicability decisions are recorded below.
- [x] Identify unresolved deployment-owned schedule, retry, and notification settings and ask targeted questions.
- [x] Record answers (A/A/A) and verify consistency with approved NFR/design artifacts.
- [x] Generate `aidlc-docs/construction/u3-p1-integration/infrastructure-design/infrastructure-design.md`.
- [x] Generate `aidlc-docs/construction/u3-p1-integration/infrastructure-design/deployment-architecture.md`.
- [x] Validate job deployment mapping against U1/U2 contracts, repository configuration, and user answers.

## Category applicability and inherited decisions

- **Deployment environment**: Reuse the existing P1 Databricks workspace/environment associated with `configs/prod.yaml`; workspace ID/region remain deployment-provided. Inherited from approved U1 design; no new environment is introduced.
- **Compute**: Reuse the approved P1 job compute policy. No U3-specific sizing or autoscaling target exists.
- **Storage**: U3 owns no data storage. U1 bronze and U2 silver/quarantine tables, checkpoint locations, and `test_prod`/`s3://test_prod` conventions remain owned by their units.
- **Messaging**: No new broker or message queue. The approved Databricks job queue is a job-native concurrency feature; Kafka source infrastructure is owned by U1.
- **Networking**: U3 has no inbound endpoint or new network route. Existing Databricks-to-Kafka reachability remains an U1 deployment concern.
- **Monitoring**: Use the approved Databricks job/task states and logs. No separate monitoring service, thresholds, or failure notifications are introduced, per answer A to Question 3.
- **Shared infrastructure**: Reuse the P1 workspace, job identity and existing access-control policy; no separate U3 identity or isolated platform resources.

## Question 1 — Daily schedule time and timezone

The functional requirement fixes a daily cadence but leaves the execution time and timezone to deployment. How should the job definition represent them?

A) Keep the daily schedule time and timezone deployment-owned; supply them through the established deployment process without inventing values in the repository. (Recommended)

B) Specify the intended local execution time (`HH:MM`) and IANA timezone (for example `Europe/Lisbon`) after `[Answer]:`.

C) Other (describe after `[Answer]:`).

[Answer]:A

## Question 2 — Job/task retry policy

NFR Design delegates retries to the deployment-configured Databricks job policy. What should this repository specify?

A) Keep retry count and delay deployment-owned under the existing P1 Databricks policy; do not invent values in the job artifact. (Recommended)

B) Specify the maximum attempts and delay between attempts after `[Answer]:`.

C) Other (describe after `[Answer]:`).

[Answer]:A

## Question 3 — Native failure notifications

Approved NFRs rely on Databricks task/job status and logs and define no alert targets. Should this job add native Databricks failure notifications?

A) No additional notification setting; use the approved status/log visibility only. (Recommended)

B) Configure native failure notifications; keep recipient values in deployment configuration and specify the recipient group/reference (not secret values) after `[Answer]:`.

C) Other (describe after `[Answer]:`).

[Answer]:A

## Existing approval gate

U3 NFR Design and its logical job/concurrency decisions are approved. All infrastructure questions are answered and consistent with those decisions. Infrastructure Design artifacts are generated and await user review and approval.

## Answers applied

- **Question 1 — Daily schedule**: A. Keep the daily execution time and timezone deployment-owned; no values are invented in the repository.
- **Question 2 — Retry policy**: A. Keep retry count and delay deployment-owned under the existing P1 Databricks policy.
- **Question 3 — Notifications**: A. Configure no additional notification setting; use approved Databricks job/task status and logs.

All answers preserve the approved NFR Design and U1/U2 infrastructure boundaries. No clarification is required.

## Stage status

- [x] Infrastructure mapping and deployment architecture generated and validated.
- [x] User approved and continued on 2026-09-24; Code Generation planning started.
