# U4 Technology Decisions — P1 Layer Timestamp Metadata

## Decisions

| Area | Decision | Rationale |
|---|---|---|
| Notebook language | Keep Python Databricks notebook source. | Both existing processing components use Python and the approved plan introduces no new runtime component. |
| Processing engine | Keep the existing Spark Structured Streaming and DataFrame APIs. | The timestamp fields belong in the established batch projection and Delta merge flow. |
| Persistence | Keep Delta tables and existing Delta merge/CDF behavior. | Bronze-to-silver integration depends on the current Delta tables; no storage technology change is needed. |
| Timestamp representation | Use the existing Spark/Delta `TIMESTAMP` type and configure timestamp generation/session interpretation for UTC. | This matches approved requirements and represents UTC instants without changing Kafka source time. |
| Schema migration | Use additive nullable column migration with type validation before batch writes. | Preserves existing data and leaves historical values NULL. Concrete DDL and CDF compatibility are implementation/design details to validate against the target Databricks runtime. |
| Dependencies | Add no package, service, or external library. | Existing Spark/Delta capabilities cover the change. |
| Testing | Use focused local tests and static checks where practical; retain Databricks-specific migration/CDF verification as pending. | The user has no Databricks environment available; no test can prove workspace runtime compatibility. |

## Constraints

- Databricks Runtime 15.4 LTS or later remains required by the existing silver `VARIANT` implementation; this work does not alter that baseline.
- Keep the existing job, configuration, secrets, checkpoint locations, and task sequence.
- Do not claim that a live Delta schema migration or notebook execution has been verified without a Databricks environment.
