# U3 P1 Integration — NFR Design Plan

## Unit context

- **Unit**: U3 — P1 Integration.
- **Scope**: One daily Databricks job coordinating U1 Bronze Ingestion then U2 Silver Processing and Quarantine.
- **Approved NFR policy**: One active job run; queue subsequent scheduled or manual triggers.
- **Dependencies**: U1 Kafka checkpoint; U2 bronze CDF checkpoint; Databricks job/task status and logs; shared environment configuration.
- **Technology constraints**: Databricks job and existing Python notebook tasks are approved. Declarative Automation Bundle YAML packaging was selected during Code Generation clarification. Exact schedule, compute, permissions, retries, and notification values remain deployment-owned per Infrastructure Design.

## Design assessment

- **Resilience**: Enforce a single active job run. Use Databricks job queueing for additional triggers. Preserve the U1/U2 durable checkpoints and task failure propagation. Queue expiry is bounded by the platform's 48-hour queue lifetime; later successful runs resume from task checkpoints subject to source retention.
- **Scalability**: Retain the approved sequential two-task model and existing distributed notebook execution. No load or growth target justifies parallel job runs or a new scaling component.
- **Performance**: Process incremental source data using U1/U2 checkpoints. No completion-time target or measured workload is available for additional tuning.
- **Security**: Use existing access controls, pass only the environment parameter, and keep secret values out of job parameters and artifacts.
- **Logical components**: Use the Databricks job's built-in concurrency and queue settings. Do not add a separate queue, cache, retry coordinator, or monitoring service.

These requirements and decisions fully specify the logical patterns; no additional design clarification is required.

## Checklist

- [x] Review the approved U3 NFR requirements and Functional Design.
- [x] Define resilience, concurrency, queue-expiry, checkpoint, and failure patterns.
- [x] Define scalability and performance patterns without unsupported numeric targets.
- [x] Define security, data-minimization, and operational-visibility patterns.
- [x] Define logical components and their interaction boundaries.
- [x] Generate `nfr-design-patterns.md` and `logical-components.md`.
- [x] Validate design against the approved U1/U2 contracts and P1 job policy.

## Deferred deployment choices

Infrastructure Design supplies the schedule time/timezone, compute configuration, job identity/grants, retry values, and notifications while preserving the single-active-run, queue-enabled, task-order, and checkpoint contracts.

## Stage status

- [x] NFR Design artifacts generated and checked against approved U3 NFR Requirements.
- [x] User approved and continued on 2026-09-24; Infrastructure Design started.
