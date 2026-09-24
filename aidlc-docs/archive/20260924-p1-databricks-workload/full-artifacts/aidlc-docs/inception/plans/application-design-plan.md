# P1 Application Design Plan

## Purpose and scope

Define the high-level components, interfaces, orchestration, and dependencies for P1. Detailed parsing, merge, checkpoint, and error-handling logic will be specified in later design stages.

## Application design checklist

- [x] Confirm component boundaries and notebook/job orchestration.
- [x] Define each component's responsibilities and external interfaces.
- [x] Define high-level method signatures, inputs, outputs, and purpose.
- [x] Define the service/job orchestration and task dependencies.
- [x] Document component dependencies and the data flow.
- [x] Generate `aidlc-docs/inception/application-design/components.md`.
- [x] Generate `aidlc-docs/inception/application-design/component-methods.md`.
- [x] Generate `aidlc-docs/inception/application-design/services.md`.
- [x] Generate `aidlc-docs/inception/application-design/component-dependency.md`.
- [x] Generate `aidlc-docs/inception/application-design/application-design.md` as the consolidated design.
- [x] Validate design completeness and consistency against approved requirements and stories.

## Proposed component boundaries

- **P1 Job**: Daily orchestration and dependency ordering for bronze and silver notebook tasks.
- **Bronze ingestion notebook**: Read incremental Kafka records and persist source payloads with Kafka metadata.
- **Silver transformation notebook**: Read bronze records, parse valid JSON, merge latest records by `event_key`, and direct malformed records to quarantine.
- **Environment configuration**: Supply Kafka hosts, topic, database, storage paths, and secret references without embedding secret values.

## Questions

### Question 1 — Job task structure
How should the daily Databricks job orchestrate the bronze and silver notebooks?

A) Use one job with sequential bronze and silver notebook tasks (Recommended; makes dependencies and task outcomes explicit)

B) Use one notebook task that runs both layers in sequence

X) Other (please describe after `[Answer]:`)

[Answer]: A

### Question 2 — Configuration interface
How should notebook components receive environment-specific settings?

A) Pass an environment name from the job and use a shared config-loading interface for `configs/{environment}.yaml` (Recommended; keeps config interpretation consistent)

B) Pass resolved non-secret settings as job parameters to each notebook

C) Have each notebook independently load its environment YAML file

X) Other (please describe after `[Answer]:`)

[Answer]: C

### Question 3 — Bronze-to-silver contract
Which interface should connect the bronze and silver components?

A) Bronze writes the Delta bronze table; silver reads that table and merges the silver table (Recommended; follows the approved bronze-to-silver flow)

B) Bronze and silver share one notebook execution and pass records directly between functions

X) Other (please describe after `[Answer]:`)

[Answer]: A

### Question 4 — Secret scope configuration
The Databricks secret key is `my-secret`, but the secret scope name is not specified. How should the scope name be supplied to the component interface?

A) Supply the scope name through environment/job configuration; notebooks retrieve the value by scope and key at runtime (Recommended; avoids hard-coding deployment-specific scope names)

B) Store the scope name in `configs/prod.yaml` and pass it through configuration

X) Other (please describe after `[Answer]:`)

[Answer]: B

## Planned design artifacts

1. `components.md` — responsibilities, boundaries, and high-level interfaces.
2. `component-methods.md` — method signatures with input/output types and purpose; detailed business logic is deferred.
3. `services.md` — Databricks job orchestration and task sequencing.
4. `component-dependency.md` — dependency matrix and data-flow diagram.
5. `application-design.md` — consolidated overview referencing the detailed artifacts.
