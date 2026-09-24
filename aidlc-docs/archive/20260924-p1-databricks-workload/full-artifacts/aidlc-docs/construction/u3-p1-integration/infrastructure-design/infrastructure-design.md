# U3 P1 Integration — Infrastructure Design

## Purpose and scope

Map the P1 integration job to the existing Databricks platform. U3 deploys one job that runs the existing U1 bronze and U2 silver/quarantine notebooks in order. It adds no data store, broker, network service, monitoring platform, compute pool, or separate workload identity.

## Infrastructure mapping

| Logical component | Infrastructure mapping | Configuration and boundary |
|---|---|---|
| P1 integration job | Databricks job defined in a Declarative Automation Bundle under `jobs/P1/` during Code Generation. | Reuse the P1 workspace/environment and approved job compute policy. Bundle target variables supply workspace-specific and deployment-owned values. |
| Bronze task | Python notebook `notebooks/P1/bronze/bronze_ingestion.py`. | First task. Uses existing Kafka configuration, Databricks Secret reference, and durable bronze checkpoint as mapped by U1. |
| Silver task | Python notebook `notebooks/P1/silver/silver_processing.py`. | Runs only after bronze succeeds. Reads bronze Delta CDF and writes silver/quarantine outputs as mapped by U2. |
| Job environment parameter | One shared environment value supplied to both notebook tasks. | Both tasks load their own `configs/{environment}.yaml`. The selected production configuration is `configs/prod.yaml`; no secret is passed as a task parameter. |
| Bronze source and output | Existing Kafka source and bronze Delta table. | Kafka route, secret access, checkpoint, table and grants remain under U1's infrastructure design. |
| Silver and quarantine outputs | Existing Delta tables in the P1 `test_prod` database/catalog convention and `s3://test_prod` storage area. | Table locations and physical catalog/schema resolution remain deployment-controlled under U2's infrastructure design. |
| Job identity and access | Shared P1 Databricks job identity and existing workspace access policy. | Preserve approved U1/U2 grants: Kafka secret and source, checkpoints, bronze read/write, silver/quarantine read/write as applicable. Do not introduce a U3 identity. |
| Queue/concurrency | Databricks job-native queueing and concurrency controls. | Maximum one active run; enable queueing for later scheduled/manual triggers. No external queue is created. |
| Operational visibility | Databricks job/task status and logs. | Use the existing platform view; no native failure recipients, custom alerts, metrics, or monitoring service are configured by this design. |

## Scheduling, retries, and run policy

- Configure one daily scheduled run, preserving the approved functional requirement.
- The exact schedule time and timezone are deployment-owned. The source-controlled job definition must receive the actual values through the established deployment process; this design does not invent them.
- Set maximum concurrent runs to one and enable the Databricks job queue, preserving the approved serialization policy. A queued run may wait up to the platform's documented 48-hour lifetime; recovery after expiry depends on the later run and the Kafka/CDF retention windows.
- Keep retry count and delay under the existing deployment-configured Databricks retry policy. Do not add notebook retry loops or duplicate retry coordination.
- Do not configure job notification recipients. Job/task state and logs remain the approved operational visibility mechanism.
- Run U1 first and U2 only after U1 succeeds. Failure of either required task must fail the overall job. Retain both durable checkpoints and never reset them during ordinary deployment.

## Runtime and data compatibility

Reuse the approved P1 job compute policy and deployment-supplied runtime selection. The selected runtime must meet the U2 requirement of Databricks Runtime 15.4 LTS or later and support the Delta `VARIANT` table feature used by silver. Deployment must confirm the feature is enabled for the silver table; doing so upgrades its Delta writer protocol and can affect older external clients. This is inherited from U2, not a new U3 runtime choice.

## Security and network boundaries

- Reuse existing workspace, catalog, table, storage, and secret access controls for the shared job identity.
- Pass only the environment name to job tasks. Never put Kafka usernames, passwords, secret values, or event payloads in bundle YAML, task parameters, or logs.
- No inbound endpoint, load balancer, API gateway, or U3-specific network route is required. U1 owns Databricks-to-Kafka DNS/routing/allowlisting; U3/U2 use the existing Databricks data plane.
- No new storage or checkpoint paths are introduced by U3. U1 and U2 own and retain their checkpoint locations.

## Deployment-owned values

The deployment process supplies the workspace/account and region, job compute policy and concrete runtime/compute, daily run time and timezone, retry count/delay, concrete catalog/schema and table locations, job identity/grants, physical checkpoint paths, and Kafka secret scope/values. The job release must render or inject values required by the target workspace without committing credentials. No assumptions are made about CI/CD tooling because none is specified in the repository.

## Applicability and extensions

- Storage, Kafka, Kafka networking, and unit-level checkpoint details are inherited from U1/U2; no U3 resource is added.
- Separate message queue, API gateway, inbound networking, custom monitoring, and notification infrastructure are not applicable to the approved workload.
- Security Baseline, Property-Based Testing, and Resiliency Baseline remain disabled; no extension-specific controls are added here.

## Validation against approved design

The mapping preserves the single daily job, sequential U1-to-U2 dependency, shared environment parameter, one-active-run maximum, native queueing, failure propagation, durable checkpoints, deployment-owned retry policy, and status/log visibility. It makes no unsupported workload sizing, completion SLA, schedule value, retry count, identity name, workspace/region, or alert target claim.
