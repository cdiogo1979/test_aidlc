# U2 Silver Processing and Quarantine — Deployment Architecture

## Environment deployment

Deploy U2 as part of the existing P1 workload to the Databricks workspace/environment associated with `configs/prod.yaml`. Workspace identity, region, runtime, compute policy, catalog resolution, and storage/table policies are supplied by deployment configuration. U2 shares the once-daily P1 job and its approved job compute policy with U1. The selected Delta `VARIANT` column requires Databricks Runtime 15.4 LTS or later and Delta variant support enabled on the silver table; enabling it upgrades the table writer protocol and may affect older external clients.

## U2 deployment path

1. Deploy the U2 Python notebook beneath `notebooks/P1/silver/` and make it available to the P1 Databricks job.
2. Pass the selected environment name through the job. U2 loads `configs/{environment}.yaml`; the current production file defines database `test_prod` and storage root `s3://test_prod`.
3. Ensure U1 enables Delta Change Data Feed on `test_prod.p1_test_kfk_brz` and the shared P1 job identity can read its CDF and write `test_prod.p1_test` and `test_prod.p1_test_kfk_quarantine` using existing Databricks catalog/table and storage grants.
4. Resolve the concrete catalog/schema names and managed/external Delta table locations through the established deployment convention. This design does not assign separate physical paths.
5. In the P1 job, run the silver task only after the bronze task succeeds. U3 owns the Bundle job definition, retry policy, environment parameter, and task dependency.
6. U2 reads bronze CDF with Structured Streaming `AvailableNow` and a stable checkpoint at `{data_path}/checkpoints/P1/silver_processing`. A new stream processes the current bronze snapshot as inserts, then future change records. On a silver/quarantine write failure, fail U2; the uncommitted CDF batch is replayed from its checkpoint and independent idempotency reconciles outputs without cross-table atomicity.
7. Use Databricks job/task status and task logs for operational visibility. Logs contain status and safe counts/source identifiers but no raw payloads or secret values.

## Resource ownership and boundaries

- The existing Databricks platform owns workspace, region, job compute policy, catalog resolution, storage, and access-control policies.
- The shared P1 job identity has the combined permissions required by U1 and U2. U2 does not itself need Kafka, secret-scope, or checkpoint access.
- U2 owns its silver and quarantine data processing contracts; table creation/location follows the established P1 deployment convention.
- U3 owns deployment of the P1 Bundle job definition and sequencing of U1 then U2.
- Kafka routing, credentials, and checkpoint remain U1/platform responsibilities.

## Deployment values to resolve

Before deployment, the platform configuration must supply concrete workspace/region, a Databricks Runtime 15.4 LTS or later, compute policy, environment, catalog/schema identifiers, physical table management/location convention, and applicable grants. Delta variant support must be enabled for the silver table. Confirm that external readers are compatible with the upgraded Delta writer protocol. Preserve the U2 CDF checkpoint and retain bronze CDF/table history for the recovery window; if CDF history expires, perform an intentional full refresh/rebuild rather than skipping data. Retry count/backoff and exact retention durations follow existing platform policies because no U2-specific values were provided.

## Shared resources and non-applicable components

U2 reuses the P1 workspace, job, job identity, catalog/database convention, storage area, and access controls. It uses its own stable checkpoint for bronze CDF, but no direct Kafka route, inbound endpoint, load balancer/API gateway, queue, dedicated workspace, isolated storage account, or separate monitoring service is required.
