# U3 P1 Integration — NFR Requirements

## Scope and source

These requirements apply to the P1 Databricks job that runs U1 Bronze Ingestion followed by U2 Silver Processing and Quarantine. They carry forward approved P1/U1/U2 NFR decisions and apply the user's concurrency decision from `aidlc-docs/construction/plans/u3-p1-integration-nfr-requirements-questions.md`.

## Requirements

| Area | Requirement | Target/status |
|---|---|---|
| Schedule | Run the P1 job once daily. | Exact execution time and timezone are deployment settings; no completion deadline is specified. |
| Concurrency and queueing | Allow at most one active run of the P1 job and enable job-run queueing for later scheduled or manual triggers. | User selected option A. Queued runs may wait up to 48 hours under current Databricks job queue behavior. |
| Performance and scale | Process available Kafka and bronze CDF increments for each run. | Daily volume, growth, and maximum completion window are unspecified; no numeric throughput or latency SLA is approved. |
| Reliability and recovery | Surface a task failure as an unsuccessful job run. A later run resumes according to the U1 Kafka checkpoint and U2 CDF checkpoint. | No uptime, bounded recovery-time, or missed-run target is specified. Retention must cover the recovery interval. |
| Queue expiry and missed triggers | If a queued run does not start before its platform queue lifetime expires, a later successful scheduled or manual run must still resume available source work using the durable checkpoints. | Databricks documents queued runs for up to 48 hours. Recovery remains subject to Kafka and bronze CDF/table retention. |
| Dependency integrity | U2 starts only after U1 succeeds; failure of either required task makes the overall job unsuccessful. | Required by approved U3 Functional Design. |
| Security and access | Use existing Databricks access controls. Do not pass secret values as job parameters or store them in job or bundle configuration. | Inherited approved P1 requirements; no additional security or compliance control was requested. |
| Observability | Databricks job/task status and logs provide initial visibility, including task failure and queued-run state. | No custom monitoring, alert recipients, or thresholds are specified. |
| Maintainability | Keep job artifacts under `jobs/P1/` and reference the approved P1 notebook/configuration interfaces. | Required by FR-01, FR-08, and repository conventions. |

## Explicitly unspecified targets

Daily input volume and growth, job completion deadline, uptime and recovery-time objectives, compute sizing, retry counts/delays, schedule time/timezone, alert thresholds, and Kafka/CDF retention durations remain unspecified. Infrastructure Design or deployment policy supplies concrete values while preserving the concurrency and checkpoint requirements above.

## Traceability

- **FR-01**: Place the P1 job artifact under `jobs/P1/` and reference the P1 tasks.
- **FR-03**: Run daily and preserve incremental progress across job runs.
- **FR-08**: Pass the selected environment to both notebook tasks.
- **U3 Functional Design**: Sequence U1 then U2 and fail the job when a required task fails.
- **U1/U2 checkpoint contracts**: Prevent concurrent P1 executions and retain source history/checkpoints for the applicable recovery window.
- **User NFR answer**: Question 1 selected A: one active run with queueing enabled.
