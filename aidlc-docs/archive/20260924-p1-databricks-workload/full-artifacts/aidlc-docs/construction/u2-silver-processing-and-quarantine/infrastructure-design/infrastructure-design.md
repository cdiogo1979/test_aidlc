# U2 Silver Processing and Quarantine — Infrastructure Design

## Deployment mapping

| Logical component | Infrastructure mapping | Configuration / deployment responsibility |
|---|---|---|
| P1 job and U2 task | Existing P1 Databricks workspace, daily job, and approved job compute policy. U3 owns the job definition and runs U2 after successful U1 completion. | Workspace/account, region, runtime, compute policy, retry settings, and selected environment come from deployment configuration. No U2-specific compute sizing is set. |
| U2 notebook | Python Databricks notebook deployed under `notebooks/P1/silver/`. | The P1 job references the notebook and passes its environment parameter. The specific filename is finalized during code generation/job integration. |
| Bronze input | Delta table `test_prod.p1_test_kfk_brz` with Change Data Feed enabled, in the existing `test_prod` catalog/database convention. | U1 enables CDF at table creation and on an existing table before further ingestion. The shared job identity needs read/change-feed access under existing catalog/table/storage policies. |
| U2 CDF checkpoint | Stable checkpoint beneath `{data_path}/checkpoints/P1/silver_processing`. | Accessible to the shared P1 job identity and retained across runs. The checkpoint must not be casually deleted or replaced. |
| Silver output | Delta table `test_prod.p1_test` in the existing `test_prod` catalog/database and `s3://test_prod` storage conventions. | The job identity needs write access and required table metadata/read access under existing grants. Managed/external location and catalog/schema resolution follow deployment configuration. |
| Quarantine output | Delta table `test_prod.p1_test_kfk_quarantine` in the same `test_prod` catalog/database and storage conventions. | The shared job identity needs write access and required table metadata/read access under existing grants. Raw payload access remains governed by existing table policies. |
| Environment configuration | `configs/{environment}.yaml`; current production configuration supplies `database: test_prod` and `data_path: s3://test_prod`. | U2 receives the environment from the P1 job and uses the existing shared configuration-loading approach. |
| Operational visibility | Existing Databricks job/task status and task logs. | Log operational status and non-sensitive counts/source identifiers. Do not log raw payloads or secrets. No separate monitoring infrastructure is added. |

## Compute and runtime

U2 runs in the shared P1 Databricks job using the existing approved job compute policy. Runtime version, cluster/serverless choice, size, autoscaling, and retry count are deployment settings. The selected Delta `VARIANT` column requires Databricks Runtime 15.4 LTS or later and Delta variant support enabled on the silver table. Enabling the feature upgrades the Delta writer protocol and may affect older external clients. No other U2-specific compute values are set because volume and completion objectives are unspecified.

## Security and access

- Reuse the shared P1 job identity. For U2, grant the access needed to read bronze and write the silver and quarantine tables under existing platform policy.
- The shared identity also has U1's separate Kafka, secret, checkpoint, and bronze permissions as required by the combined job; U2 itself does not connect to Kafka or use the U1 checkpoint.
- Use existing Databricks workspace, catalog/table, and storage access controls. This design adds no new classification, encryption, or compliance assumptions.
- Keep secret values and raw payloads out of notebook source, Bundle YAML, checked-in configuration, and task logs. Raw payloads are persisted only in the access-controlled quarantine table when required by the functional contract.

## Networking and messaging

U2 reads bronze CDF and writes silver/quarantine through the existing Databricks/Delta data plane. It has no inbound endpoint and makes no direct Kafka connection. U1 owns Kafka DNS, routing, broker allowlisting, secret access, Kafka checkpoint access, and enabling CDF on bronze. No new queue, proxy, API gateway, load balancer, or network appliance is required.

## Storage and lifecycle

Silver and quarantine use the existing `test_prod` catalog/database and `s3://test_prod` storage conventions. The U2 streaming checkpoint uses the stable `{data_path}/checkpoints/P1/silver_processing` path; do not remove or replace it during normal deployments. The exact catalog/schema identifier and whether each Delta table is managed or external are determined by deployment convention; no separate table locations were requested. Apply existing table/platform retention policies without removing current silver state or quarantine data within the required diagnostic/replay horizon. Bronze CDF and source table history retention must be long enough for the scheduled stream's recovery window. No exact retention duration was approved.

## Operational behavior

Databricks task status and logs provide initial operational visibility. A CDF read or either output write failure fails the U2 task. Silver and quarantine are independent writes without a cross-table transaction; if one succeeds before the other fails, the P1 retry policy can replay the CDF batch from its checkpoint and idempotent source identity handling reconciles outputs. Do not configure the stream to ignore missing CDF history. No separate monitoring stack or custom alert target is introduced.

## Resource ownership and boundaries

- The platform owns the shared Databricks workspace, job compute policy, catalog and storage policies, and physical table conventions.
- U2 owns the silver transformation task and its logical silver/quarantine table use.
- U3 owns the daily P1 Bundle job definition, environment parameter propagation, and U1-before-U2 dependency.
- U1 owns Kafka connectivity, secrets, Kafka checkpointing, bronze ingestion, and enabling CDF on bronze.

## Out of scope

No dedicated workspace or identity, new storage account, explicit cluster profile, new network route, separate checkpoint, queue, or monitoring service is introduced for U2.
