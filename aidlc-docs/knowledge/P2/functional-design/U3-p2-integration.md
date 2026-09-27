# U3 P2 Pipeline Integration — Functional Design

## Purpose and boundary

Orchestrate P2 bronze and silver as a separate daily Databricks job. U3 owns task order, environment/parameter propagation, schedule, retry settings, and overall run outcome. U1 owns Kafka ingestion; U2 owns current-state processing and quarantine.

## Inputs and outputs

- **Trigger**: Daily schedule or manual invocation.
- **Parameters**: `environment` defaulting to `prod`, `bronze_lookback_days` defaulting to `0`, and `silver_lookback_days` defaulting to `0`.
- **Tasks**: P2 bronze followed by P2 silver.
- **Bundle/job**: `jobs/P2/databricks.yml`; bundle `p2_databricks_workload`; job `P2 Daily Pipeline`.

## Business rules

1. Run bronze first and start silver only after bronze succeeds.
2. Both notebooks load the shared production config independently; secrets and records are not job parameters.
3. Use P2-specific tables and checkpoints for all task state.
4. Preserve P1-equivalent schedule, runtime/compute policy, run-as identity, retry controls, and task parameter names/defaults. Their deployment values are required inputs.
5. A task failure makes the job fail; never report success after an incomplete pipeline.

## Deployment and verification boundary

Bundle validation and runtime execution in the target Databricks workspace remain unverified under the user's accepted verification waiver. Deployment instructions require resolving environment variables, permissions, topic, secrets, storage, and recovery ownership before deployment or schedule enablement.
