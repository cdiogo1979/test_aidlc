# Technology Stack Decisions: P1 Streaming Lookback

## Decisions

| Area | Decision | Rationale |
|---|---|---|
| Notebook runtime | Existing Databricks Python notebooks and Structured Streaming | Preserve established P1 execution model and `AvailableNow` triggers. |
| Bronze source | Existing Spark Kafka source using its starting timestamp option for new queries | Uses Kafka record time for the approved bronze lookback semantics. |
| Silver source | Existing Delta Change Data Feed streaming source using `startingTimestamp` for new queries | Uses bronze CDF commit time for the approved silver lookback semantics. |
| Checkpoint storage | Existing per-layer S3 checkpoint paths | Keep the established checkpoint ownership and reset only the selected layer's path. |
| Output persistence | Existing Delta `MERGE` operations and source identity rules | Replay remains idempotent without schema or storage-model changes. |
| Orchestration | Existing Databricks Declarative Automation Bundle job | Expose separate job-level `bronze_lookback_days` and `silver_lookback_days` parameters, both defaulting to zero; preserve bronze-before-silver dependency and existing `environment` parameter. |
| Replay throttling | No new source rate limits | User selected existing `AvailableNow` throughput behavior; capacity varies with source range. |
| Replay observability | Databricks task logs | User selected run-log summaries; no new audit table or monitoring service. |

## Rejected Additions

- No new libraries, services, tables, infrastructure resources, or monitoring integrations.
- No configured lookback cap or per-trigger rate limit.
- No production or Databricks runtime test environment is assumed.

## Verification Boundary

The stack choices are based on current repository patterns. They do not establish that the timestamp options, source retention behavior, job parameters, or recursive checkpoint deletion have been validated in a live Databricks workspace.
