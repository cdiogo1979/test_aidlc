# U1 Bronze Ingestion — Deployment Architecture

## Environment deployment

Deploy the P1 workload to the existing Databricks workspace and environment associated with `configs/prod.yaml`. The workspace identifier and region are resolved by deployment configuration; they are not stored in the repository plan. The same P1 workspace/job framework supplies the approved job compute policy and runtime settings.

## U1 deployment path

1. Deploy the U1 Python notebook to `notebooks/P1/bronze/` and make it available to the P1 Databricks job task.
2. Pass the environment name to the job task. U1 loads `configs/{environment}.yaml` and reads the Kafka broker setting, database, storage root, and secret reference from that file.
3. Provision the Databricks secret scope/key externally. The configured key name is `my-secret`; secret material is not part of repository configuration.
4. Ensure the workspace has the existing approved route and broker allowlist to reach Kafka at `test.com:9995` and topic `my-topic`.
5. Ensure the job identity can read the configured secret, access the stable checkpoint subpath beneath `s3://test_prod`, and write the bronze Delta table `test_prod.p1_test_kfk_brz` using existing workspace, catalog, and storage grants.
6. Run U1 as the bronze task in the daily P1 job. U3 defines the job in the P1 Declarative Automation Bundle and ensures U2 starts only after U1 succeeds.
7. Databricks job/task status and logs expose execution outcomes. A failed task uses the job's configured retry policy; the stable checkpoint supports resuming committed progress.

## Resource ownership and boundaries

- The existing Databricks platform owns workspace, account/region, workspace policy, and job compute policy.
- The P1 workload owns its notebook artifact and logical table/checkpoint usage.
- Environment/deployment configuration owns environment-specific workspace selection, secret scope, runtime/compute selections, catalog resolution, checkpoint URI, and access grants.
- U3 owns the daily Bundle job definition and task dependency ordering.
- Kafka cluster operations and broker allowlisting are managed by the existing Kafka/platform owners.

## Deployment values to resolve

Before provisioning/running the job, deployment configuration must provide the concrete workspace and region, runtime/compute policy, catalog/schema mapping, secret scope, and stable checkpoint URI beneath the approved S3 storage root. Retention and retry count/backoff follow established platform policies because the user supplied no workload-specific values.

## Shared resources and non-applicable components

U1 uses the existing shared P1 workspace, catalog/database convention, storage area, Kafka service, and access controls. It does not require a dedicated workspace, API gateway, load balancer, additional queue, or separate monitoring service. The P1 scheduled notebook has no inbound service endpoint.
