# U2 Silver Processing and Quarantine — Infrastructure Design Plan

## Unit context

- **Unit**: U2 — Silver Processing and Quarantine.
- **Functional/NFR design**: U2 reads bronze Delta data, writes silver and quarantine Delta tables idempotently, and fails visibly on read/output errors. No cross-table transaction is assumed.
- **Shared P1 platform**: One daily Databricks job runs bronze before silver. U1 infrastructure design maps the job to the existing P1 Databricks workspace/environment, approved job compute policy, `test_prod` catalog/database convention, and `s3://test_prod` storage area; concrete workspace, runtime, physical table locations, and grants follow deployment configuration.
- **U2 resources to map**: Silver table `test_prod.p1_test`, quarantine table `test_prod.p1_test_kfk_quarantine`, and the U2 notebook under `notebooks/P1/silver/`.
- **Scope**: Map U2 to shared infrastructure and identify U2-specific table storage and access boundaries. U3 owns the P1 Bundle job and U1 owns the Kafka route/checkpoint.

## Infrastructure assessment checklist

- [x] Confirm U2 deployment environment and reuse of the shared P1 Databricks workspace/job compute.
- [x] Map silver and quarantine tables to the established catalog/database and storage conventions.
- [x] Define the U2 job identity's read/write access boundaries.
- [x] Evaluate network, messaging, and monitoring infrastructure applicability.
- [x] Define shared infrastructure ownership and resource isolation.
- [x] Generate U2 `infrastructure-design.md` and `deployment-architecture.md`.
- [x] Validate mapping against approved U2 designs, U1 shared-platform decisions, and repository configuration.

## Answers applied

Question 1 selected A: reuse the `test_prod` catalog/database and `s3://test_prod` storage conventions, with concrete catalog/schema and table locations resolved through deployment policy. Question 2 selected A: reuse the shared P1 job identity with the required read/write grants for U2.

## Code generation constraint update

During U2 Code Generation planning, the user selected a Delta `VARIANT` attributes column. Deployment therefore requires Databricks Runtime 15.4 LTS or later and Delta variant table support enabled; enabling it upgrades the Delta writer protocol and may affect older external clients. This constraint is carried into the infrastructure mapping and deployment values.

## Question 1 — Silver and quarantine table placement

U1 uses the existing `test_prod` catalog/database convention and `s3://test_prod` storage area, with physical table locations following deployment convention. Should U2 use that same placement for both output tables?

A) Yes. Use the existing `test_prod` catalog/database and storage conventions; resolve concrete catalog/schema and managed/external table locations through deployment configuration (Recommended; keeps P1 data on its shared platform).

B) Specify a separate catalog/schema or physical storage location for silver and/or quarantine after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — U2 job identity and grants

How should the daily P1 job identity access U2 resources?

A) Reuse the shared P1 job identity, granting it read access to bronze and the existing required write/read access to silver and quarantine under platform policy (Recommended; matches the single P1 job boundary).

B) Use a distinct U2 identity; specify the required identity and access boundary after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Inherited decisions and category applicability

- **Deployment environment**: Reuse the existing P1 Databricks workspace/environment associated with `configs/prod.yaml`, as approved for U1. U2 is part of the same P1 workload/job.
- **Compute**: Reuse the approved P1 Databricks job compute policy; runtime and sizing are deployment settings, with no U2-specific target.
- **Networking**: No new network path is required. U2 reads/writes Databricks Delta data and has no direct Kafka connection or inbound endpoint. U1 owns Kafka routing.
- **Messaging**: No new queue or messaging infrastructure; bronze Delta is U2's input boundary.
- **Monitoring**: Databricks job/task status and logs; no additional monitoring or alerting service is approved.
- **Shared infrastructure**: Reuse the P1 workspace, job, catalog/database, storage area, and existing access-control framework. No dedicated workspace or storage account is in scope.
