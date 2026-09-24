# P1 Application Design

## Overview

P1 is a daily Databricks workload organized as one job with two sequential notebook tasks. The bronze notebook reads incremental Kafka records and persists the original payload with Kafka metadata. The silver notebook reads bronze, expands valid JSON, maintains the latest row per `event_key`, and quarantines malformed records.

## Components and boundaries

- **P1 Daily Job**: A Databricks Declarative Automation Bundle schedules the workload and runs bronze before silver; deployment variables supply environment-specific settings.
- **Bronze Ingestion Notebook**: Owns Kafka access and source-record persistence.
- **Silver Transformation Notebook**: Owns JSON expansion, current-state merge, and malformed-record routing.
- **Environment Configuration**: Each notebook independently loads `configs/{environment}.yaml`.
- **Databricks Secret Store**: Provides the Kafka credential at runtime; the scope name is held in environment config and the key is `my-secret`.
- **Delta Tables**: Bronze is the persisted handoff between notebooks; silver and quarantine are silver-task outputs.

## Orchestration and interfaces

The job passes `environment=prod` to each notebook. The bronze task runs first; silver depends on bronze task success. Both notebooks independently load the selected environment YAML. The bronze-to-silver contract is the persisted bronze Delta table, not in-memory record passing.

High-level notebook interfaces:

- `run_bronze_ingestion(environment: str) -> BronzeWriteSummary`
- `run_silver_transformation(environment: str) -> SilverRunSummary`

Concrete configuration and result type schemas are deferred to Units Generation and Functional Design.

## Design decisions

- One daily Databricks job with separate sequential bronze and silver tasks.
- Each notebook loads the environment YAML independently; job parameters carry the environment name.
- The bronze Delta table is the interface between layers.
- The Kafka secret scope name is configured in `configs/{environment}.yaml`; secret value remains in Databricks Secrets under key `my-secret`.
- Detailed Kafka offsets, checkpointing, schema handling, merge rules, retries, and quarantine implementation are deferred to later design stages.

## Traceability

- Requirements: FR-02 through FR-08.
- User stories: US-P1-01 and US-P1-02.
- Detailed component definitions: `components.md`.
- Method interfaces: `component-methods.md`.
- Orchestration: `services.md`.
- Dependencies and data flow: `component-dependency.md`.
