# U1 Bronze Ingestion — Infrastructure Design Plan

## Unit context

- **Unit**: U1 — Bronze Ingestion.
- **Known infrastructure**: Databricks workload; Kafka topic `my-topic`; configured broker `test.com:9995`; secret key `my-secret`; bronze Delta table `test_prod.p1_test_kfk_brz`; environment file currently provides `database: test_prod` and `data_path: s3://test_prod`.
- **Logical components**: Daily Databricks job task, Python notebook, Kafka source, durable streaming checkpoint, bronze Delta table, Databricks Secrets, task status/logs.
- **Design boundary**: Map logical components to deployed resources. Do not invent a Databricks workspace/region, compute shape, Unity Catalog mapping, checkpoint URI, or network route if not supplied. The P1 Bundle job is owned by U3, while U1's deployment requirements are recorded here.

## Infrastructure assessment checklist

- [x] Identify the target Databricks workspace/account, cloud region, and environment.
- [x] Identify compute policy/runtime constraints for the U1 job task.
- [x] Map bronze table and checkpoint storage to the catalog/schema and S3 path conventions.
- [x] Confirm Kafka broker reachability and required network/security configuration from Databricks.
- [x] Confirm use of shared workspace, catalogs, storage, and access boundaries.
- [x] Map observability to existing Databricks job status and task logs; no separate monitoring stack is currently required.
- [x] Confirm no load balancer/API gateway is needed because U1 exposes no inbound service endpoint.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/infrastructure-design/infrastructure-design.md`.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/infrastructure-design/deployment-architecture.md`.
- [x] Validate the infrastructure mapping against approved functional and NFR designs and repository configuration.

## Question 1 — Deployment environment

Where should U1 be deployed?

A) Use the existing P1 Databricks workspace/environment associated with the current `prod.yaml`; workspace identifier and region are provided by deployment configuration.

B) Specify the target cloud account/workspace, region, and environment after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Compute infrastructure

What compute should the daily U1 task use?

A) Use the existing approved Databricks job compute policy; choose runtime and size through deployment configuration, with no U1-specific sizing target.

B) Specify a required job cluster or serverless policy, runtime version, and sizing/autoscaling bounds after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 3 — Bronze table and checkpoint storage

How should the bronze table and durable checkpoint be mapped to deployed storage?

A) Use the existing `test_prod` database/catalog convention and `s3://test_prod` storage area; select the concrete checkpoint subpath through the existing deployment convention.

B) Specify the Unity Catalog catalog/schema, table location, and exact checkpoint URI after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 4 — Kafka connectivity

What network path should Databricks use to reach Kafka at `test.com:9995`?

A) Use the existing approved Databricks-to-Kafka network route and broker allowlist; no new network components are required for U1.

B) Specify required private connectivity, firewall/allowlist, DNS, or broker-side changes after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 5 — Shared infrastructure and access boundaries

How should U1 use shared workspace, catalog, and storage resources?

A) Use existing P1 workspace policies, catalog/table grants, and storage access controls; grant the job identity only the access already approved for this workload.

B) Require isolated workspace/catalog/storage resources or additional role boundaries; specify them after `[Answer]:`.

C) Other (please describe after `[Answer]:`)

[Answer]: A

## Category applicability decisions

- **Monitoring infrastructure**: No additional question is needed; approved NFR Requirements specify Databricks job status and task logs, with no separate monitoring service or alerting requirement.
- **Load balancing/API gateway**: Not applicable; U1 is a scheduled data-ingestion task and exposes no inbound API or service endpoint.
- **Messaging infrastructure**: Kafka is the approved existing source, including topic, broker setting, and secret reference. Question 4 addresses its infrastructure connectivity; no additional queue or broker is proposed.
