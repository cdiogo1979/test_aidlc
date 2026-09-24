# U3 P1 Integration — Deployment Architecture

## Deployment topology

Deploy one P1 Databricks job to the existing P1 workspace/environment using the Declarative Automation Bundle under `jobs/P1/`. It uses the approved shared job compute policy and shared P1 job identity, with deployment-owned values supplied by bundle variables. The bundle references the existing notebooks:

1. `notebooks/P1/bronze/bronze_ingestion.py` — U1 Bronze task.
2. `notebooks/P1/silver/silver_processing.py` — U2 Silver task, dependent on successful U1 completion.

Both tasks receive the same environment name and independently load the matching `configs/{environment}.yaml`. No data payload or credential is passed between tasks. Bronze Delta is the persisted handoff from U1 to U2.

## Job execution and recovery

The job runs once per day. Deployment supplies the execution time and timezone. Databricks job settings enforce at most one active run and queue subsequent scheduled/manual triggers. U2 has an explicit dependency on U1 success. Either task failure leaves the job unsuccessful and visible in Databricks task/job status and logs.

Task retries follow the deployment-configured Databricks retry policy. Later retries or scheduled runs rely on U1's Kafka checkpoint and U2's CDF checkpoint; deployment must keep the corresponding Kafka and Delta CDF history available for the intended recovery window. Queued runs can expire after up to 48 hours, after which a later successful run resumes only the source work still available under those retention contracts.

## Shared data and access plane

- U1 owns Kafka connectivity, secret access, bronze writes, and the bronze checkpoint.
- U2 reads bronze CDF and owns silver/quarantine writes and its CDF checkpoint.
- Existing P1 catalog/database and storage conventions are reused. Concrete schema/table locations and physical checkpoint paths come from deployment configuration.
- The shared job identity uses existing approved grants for both tasks; no separate U3 identity or isolated data plane is introduced.
- The selected deployment runtime must be Databricks Runtime 15.4 LTS or later and support Delta `VARIANT` for U2. Enable the feature on the silver table according to platform deployment procedure and account for its writer protocol compatibility impact.

## Environment-specific deployment inputs

Workspace/account and region, concrete compute/runtime settings, daily schedule time/timezone, retry count/delay, job identity/grants, catalog/schema and table locations, checkpoint paths, and Kafka secret references are supplied or rendered by the deployment process. Actual secret values remain in Databricks Secrets. The repository currently supplies `configs/prod.yaml`; it does not identify the workspace, select a compute shape, or define the schedule or retry values.

No custom alert recipients or separate monitoring platform are configured. Operators use Databricks job/task status and logs.

## Release constraints

- Deploy the job definition without resetting U1/U2 checkpoints during routine updates.
- Preserve maximum concurrent runs of one, job queueing, the daily cadence, and the U1-before-U2 dependency.
- Ensure deployment-provided schedule, retry, identity, storage, and runtime values satisfy the approved NFR and unit contracts before enabling the schedule.
- Keep notebook source and the bundle definition under the repository paths defined by `AGENTS.md`; keep environment-varying values in `configs/` or bundle target/deployment variable inputs.
