# U3 P1 Integration — Logical Components

## Components

| Component | Responsibility | Reliability / security boundary |
|---|---|---|
| P1 Databricks job | Starts U1, then U2 after U1 success; supplies the selected environment value to both tasks and reports the overall run outcome. | Maximum one active run; built-in job queueing enabled. Uses existing job identity/access policy. |
| Databricks job queue/concurrency controls | Serializes later scheduled or manual run triggers behind an active P1 job run. | Queued run lifetime is up to 48 hours under documented platform behavior. No separate queue service is deployed. |
| U1 Bronze task | Reads Kafka and writes raw payload plus metadata to bronze Delta. | Owns its durable Kafka checkpoint. Failures block U2 and fail the job. |
| U2 Silver task | Reads bronze Delta CDF and writes silver and quarantine outputs. | Runs only after U1 succeeds; owns its durable CDF checkpoint. Failures fail the job. |
| Environment configuration | Supplies deployment-specific settings selected by the shared environment parameter. | Both tasks load the same environment file independently; no credential value is passed as a job parameter. |
| Databricks job/task status and logs | Exposes queued, running, successful, and failed job/task states and operational diagnostics. | Existing visibility approach; no separate monitoring or alert component is added. |

## Interaction and recovery flow

1. Databricks accepts a scheduled or manual P1 trigger. If another run is active, the built-in queue holds the trigger according to the approved queue policy.
2. The job passes one environment value to U1 and starts it as the first task.
3. After U1 succeeds, the job starts U2 with the same environment value. The bronze Delta table is the persisted handoff.
4. Each notebook reads or advances only its own checkpoint while processing its task input.
5. The job reports success only after both tasks succeed; a task failure remains visible as a failed job run.
6. A retry or later run resumes using the durable checkpoints. If a queued run expires after the platform queue lifetime, a later run can recover only while the source retention contracts remain satisfied.

## Components intentionally not introduced

No external queue, cache, circuit breaker, retry coordinator, custom monitoring service, or event payload transfer between tasks is introduced. Job-native queueing, task dependencies, Databricks status/logs, and U1/U2 checkpoints meet the approved scope.

## Deployment boundary

This is a logical design. Schedule time/timezone, compute choice, job identity and grants, retry configuration, notification policy, and source retention duration are supplied by Infrastructure Design or platform policy.
