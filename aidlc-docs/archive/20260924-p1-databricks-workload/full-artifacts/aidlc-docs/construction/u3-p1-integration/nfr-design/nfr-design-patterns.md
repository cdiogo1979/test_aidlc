# U3 P1 Integration — NFR Design Patterns

## Resilience and recovery

- Configure the P1 job for at most one active run and enable Databricks job queueing for subsequent scheduled or manual triggers. This serializes both tasks and prevents concurrent access to their shared checkpoints and tables.
- Keep the job's U1-before-U2 dependency. A failed U1 task blocks U2; a failed required task leaves the overall job failed.
- Preserve U1's Kafka checkpoint and U2's bronze CDF checkpoint across runs. Do not reset checkpoints during normal deployment or recovery.
- Let the deployment-configured retry policy handle task retries; do not add independent retry loops or retry coordination to the notebooks.
- Databricks queues a blocked job run for up to 48 hours. If a queued run expires or a schedule is missed, a later successful run resumes available work from the durable checkpoints, provided Kafka offsets and bronze CDF/table history remain available for the recovery window.
- Do not claim a cross-task transaction or platform-wide exactly-once behavior. Task/job status must reflect failures.

## Scalability

- Keep the single daily P1 job and its sequential bronze and silver tasks.
- Use existing Databricks distributed execution for task-level processing. Do not increase concurrent job runs to scale a workload that shares checkpoints and state.
- No input volume, growth curve, or scaling trigger is specified. Defer compute sizing and any capacity limits until representative run data and deployment policy are available.

## Performance

- Process available Kafka and bronze CDF increments through the existing checkpointed U1/U2 notebook flows.
- Avoid adding parallel task branches, full-history rescans, custom caching, or unmeasured tuning.
- No numeric runtime or completion SLA is asserted. Review actual task durations and volumes before proposing performance targets.

## Security and configuration

- Use existing approved Databricks access controls for the job identity, notebooks, tables, secrets, and checkpoint paths.
- Pass only the shared environment name to the two notebook tasks. Each task independently loads its environment configuration.
- Do not pass Kafka credentials, raw events, or other secret material in job parameters, source artifacts, or logs.
- Do not introduce new security, compliance, or encryption claims beyond existing platform protections.

## Operational visibility

- Use Databricks job/task state and logs to expose task failures and queued runs.
- Preserve failed task outcomes; do not mark the pipeline complete if U1 or U2 fails.
- No custom metrics, alert targets, thresholds, or separate monitoring service are introduced.

## Queue and retention boundary

Queueing is a built-in job setting, not a separate message queue. Its documented waiting lifetime is up to 48 hours. Kafka retention, Delta CDF/table retention, and both checkpoints must support the recovery interval; exact retention durations remain deployment policy. If U2 cannot read required CDF history, it fails visibly according to its approved contract.

## Applicability summary

Security Baseline, Property-Based Testing, and Resiliency Baseline extensions remain disabled. No extension-specific rules apply. These patterns implement the approved P1 NFR requirements and existing U1/U2 contracts.
