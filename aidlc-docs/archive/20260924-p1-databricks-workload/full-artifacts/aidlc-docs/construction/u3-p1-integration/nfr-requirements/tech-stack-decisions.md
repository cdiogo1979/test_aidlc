# U3 P1 Integration — Technology Decisions

## Decisions

| Concern | Decision | Rationale / constraint |
|---|---|---|
| Job platform and artifact | Databricks job defined through Declarative Automation Bundle YAML under `jobs/P1/`. | User selected bundle variables/targets during U3 Code Generation clarification; this supersedes the earlier JSON packaging choice while preserving the Databricks job contract. |
| Task form | Python notebook tasks referencing the existing U1 and U2 notebooks. | Existing task interfaces and approved unit boundaries. |
| Task dependency | U2 depends on successful completion of U1. | Prevents silver from processing before bronze persistence succeeds. |
| Environment propagation | Pass the same environment value to both tasks; notebooks load their own environment YAML. | Approved Application Design and U3 Functional Design. |
| Maximum concurrent runs | Set the P1 job maximum concurrent runs to `1`. | User selected one active P1 run to serialize access to the shared Kafka and CDF checkpoints. |
| Job queueing | Enable queueing for later scheduled/manual triggers. | User selected queueing instead of immediately skipping an overlapping trigger. Databricks documents queueing up to 48 hours when a run cannot start. A later run still depends on source/checkpoint retention. |
| Monitoring and failure reporting | Use Databricks job/task statuses and logs. | Inherited from approved U1/U2 NFR requirements; no separate monitoring service was requested. |

## Decisions deferred

Exact daily cron expression and timezone, compute policy/selection, job identity and grants, retry settings, notifications, and deployment-specific configuration values are deferred to U3 Infrastructure Design or platform policy. No new library, cluster shape, or runtime version is selected here.

## Reference

- Databricks documents the job-level queue setting, queue lifetime, and maximum concurrent runs in [Configure and edit Lakeflow Jobs](https://docs.databricks.com/aws/en/jobs/configure-job).
