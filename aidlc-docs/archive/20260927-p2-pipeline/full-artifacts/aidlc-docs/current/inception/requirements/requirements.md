# Requirements: P2 Databricks Pipeline

## Intent Analysis

- **User request**: Create a new pipeline P2 that is the same as P1 except it reads a different Kafka topic.
- **Request type**: New workload, implemented as a copy of the existing P1 Databricks workload.
- **Scope estimate**: Multiple workload artifacts — configuration, two notebooks, and a Databricks bundle job.
- **Complexity estimate**: Simple, with deployment and data-isolation considerations.

## Functional Requirements

1. P2 must preserve P1's daily orchestration and bronze-then-silver task dependency.
2. P2 must use Kafka topic `my-test-p2`; P1 continues to use its existing topic.
3. P2 must preserve P1's ingestion, source metadata, CDF, replay/lookback, JSON validation, current-state, quarantine, and timestamp behavior.
4. P2 must have its own `jobs/P2/` bundle, job/resource names, and `notebooks/P2/bronze/` and `notebooks/P2/silver/` notebooks.
5. P2 must use the shared `configs/prod.yaml` used by all projects. Preserve the existing `kafka.topic` default for P1 and add a `kafka.topics_by_project.P2` override set to `my-test-p2`. P2 selects its override while using the same `prod` environment profile and other shared Kafka settings.
6. P2 must use P2-specific bronze, silver, quarantine, and checkpoint names/paths so the new workload does not write into P1's persisted state. Other environment values remain equivalent to P1 unless needed for deployment-specific inputs.
7. P2's job must preserve P1's schedule, parameter names and defaults, run-as, cluster policy/runtime inputs, retry settings, environment profile (`prod`), and execution ordering.
8. P1 artifacts and behavior must remain unchanged.

## Non-Functional Requirements and Constraints

- Do not place credentials or secret values in checked-in files; preserve P1's secret reference pattern.
- Maintain the repository's six-section Databricks notebook structure, Google-style docstrings, and Python quality conventions.
- Keep P2 changes additive and independently deployable through its own bundle.
- P2 uses the same deployment-provided environment inputs and runtime constraints as P1; no new infrastructure policy is introduced.
- Databricks, Kafka, and storage integration behavior cannot be confirmed without the deployment environment.

## Scenarios and Acceptance Criteria

- A P2 daily run consumes only `my-test-p2`, writes P2-owned bronze data, then processes that data into P2 silver and quarantine outputs.
- Retrying P2 or running a configured lookback uses P2-owned checkpoints and tables without resetting or modifying P1 progress.
- P1 configuration, topic, tables, checkpoints, and job remain unchanged.
- P2 bundle paths resolve to P2 notebooks and P2 configuration is selected by the copied P2 notebooks.

## Extension Configuration

- Security Baseline: disabled by user choice.
- Property-Based Testing: partial enforcement for pure functions and serialization round-trips; only applicable rules PBT-02, PBT-03, PBT-07, PBT-08, and PBT-09 are blocking.
- Resiliency Baseline: disabled by user choice.
