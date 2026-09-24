# U1 Bronze Ingestion — Infrastructure Design

## Deployment mapping

| Logical component | Infrastructure mapping | Configuration / deployment responsibility |
|---|---|---|
| P1 job and U1 task | Existing P1 Databricks workspace and its approved job compute policy. | Workspace/account, region, selected runtime, compute policy, and environment are supplied by deployment configuration. The job definition itself is delivered by U3. |
| U1 notebook | Python Databricks notebook deployed under `notebooks/P1/bronze/`. | Notebook path and task parameters are referenced by the P1 job. |
| Kafka source | Existing Kafka cluster, topic `my-topic`, broker setting `kafka.hosts` (`test.com:9995`). | Use the existing approved Databricks-to-Kafka route, DNS, and broker allowlist. No new networking resource is introduced by U1. |
| Kafka credentials | Existing Databricks Secrets scope/key reference; key name is `my-secret`. | Secret scope and secret value are provisioned outside repository files. The job identity must be allowed to read the configured secret. |
| Environment settings | `configs/{environment}.yaml`; current production file contains `database: test_prod` and `data_path: s3://test_prod`. | Workspace/job passes the selected environment. Environment-specific values are managed in configuration/deployment. |
| Bronze data | Delta table `test_prod.p1_test_kfk_brz` in the existing `test_prod` database/catalog convention. | Use the existing catalog/schema grants and table/storage access policy. Exact catalog resolution and physical table location follow the deployment's established convention. |
| Streaming checkpoint | Durable checkpoint in the configured S3 storage area rooted at `s3://test_prod`. | Exact checkpoint subpath and lifecycle follow the existing deployment convention; no exact URI or retention period was provided. The path must be stable across task runs and accessible to the job identity. |
| Operational visibility | Databricks job/task status and task logs. | No separate monitoring service, custom alert destination, or threshold is required in this design. |

## Compute and runtime

U1 uses the P1 workspace's existing approved Databricks job compute policy. Runtime version, cluster/serverless choice, sizing, and scaling are deployment settings; this design sets no U1-specific values because workload volume and performance objectives are unspecified.

## Security and access

- Use the existing workspace identity/access controls and approved network route.
- Grant the job identity the access required for the configured secret, Kafka source, checkpoint path, and bronze destination under existing deployment policy.
- Do not store secret values in Git, notebook source, the Databricks Bundle, or logs.
- Use existing catalog/table and S3 access controls; this design does not assume unprovided encryption or compliance configuration.

## Networking and messaging

Kafka remains the existing external source. Databricks reaches `test.com:9995` over the approved existing route and broker allowlist. No queue, proxy, load balancer, API gateway, or new network appliance is required for this scheduled workload. Connectivity/DNS and broker allowlist must be present in the target workspace environment.

## Storage and lifecycle

The bronze table follows the `test_prod` database/catalog convention and stores Delta records as specified by the U1 contract. The streaming checkpoint uses a stable subpath beneath the configured `s3://test_prod` area. The concrete catalog identifier, table location, checkpoint URI, and lifecycle/retention are deployment conventions not supplied by the answers and remain open implementation configuration values.

## Operational behavior

Databricks task outcome and logs provide the initial operational signal. Kafka read or bronze write failure fails the U1 task. The P1 job's configured retry policy can rerun the task, and the stable checkpoint resumes committed progress. U1 does not skip failed input or add notebook-level retries.

## Out of scope

No dedicated workspace, new Kafka cluster, new network path, custom compute profile, load balancer, API gateway, separate monitoring stack, or isolated P1 storage account is introduced.
