# Code Generation Plan: P2 Pipeline

**Unit**: `p2-pipeline` (bronze ingestion, silver processing/quarantine, and daily job)

**Dependencies**: Approved requirements, P1 canonical U1/U2/U3/U4 designs, approved P2 Functional Design, and approved NFR framework choice.

**Contracts**: Kafka topic `my-test-p2`; shared `prod` config with a P2 topic override, P2-specific tables/checkpoints/job/notebook paths; identical P1 processing semantics and schedule/job controls. P1 workload files remain unchanged.

## Steps

1. [x] **Add the approved PBT development dependency** — update `requirements-dev.txt` with pinned `hypothesis==6.168.1` (NFR decision; PBT-09).
2. [x] **Extend the shared production configuration** — preserve `configs/prod.yaml` for all projects and retain its existing `kafka.topic` value for P1; add `kafka.topics_by_project.P2: my-test-p2`. Keep all shared Kafka hosts/security/secret references and use the same `prod` environment profile.
3. [x] **Create P2 bronze notebook** — copy `notebooks/P1/bronze/bronze_ingestion.py` to `notebooks/P2/bronze/bronze_ingestion.py`; preserve ingestion logic, but use `P2_PROJECT_ROOT`, add a small pure topic resolver that selects the explicit `topics_by_project.P2` override and fails clearly if it is missing, use the P2 bronze table and `checkpoints/P2/bronze_ingestion`, and update the Information cell.
4. [x] **Create P2 silver notebook** — copy `notebooks/P1/silver/silver_processing.py` to `notebooks/P2/silver/silver_processing.py`; update Information/project-root text, use P2 bronze/silver/quarantine identifiers, and `checkpoints/P2/silver_processing`. Keep the environment default `prod`; preserve transformations and six-cell layout.
5. [x] **Create P2 bundle and job resource** — add `jobs/P2/databricks.yml` and `jobs/P2/resources/p2-daily-pipeline.yml`, preserving P1 schedule, parameter names/lookback defaults, task dependency, and preserving the `prod` environment default, retries, run-as, and cluster policy/runtime variables while changing bundle/job/cluster identifiers and notebook paths to P2.
6. [x] **Add the P2 property test** — create `tests/test_p2_pipeline_properties.py`. Use Hypothesis with a domain-specific generated string containing arbitrary surrounding text and a quote or backslash. Extract `_project_kafka_topic` and `_jaas_quote` from the P2 notebook AST so importing Spark/Databricks modules is unnecessary. Assert both the project-topic override invariant and the escaping invariant against simple contracts. Use `@settings(derandomize=True)` and leave shrinking enabled (PBT-03, PBT-07, PBT-08).
7. [x] **Run the test suite in CI** — update `cicd/Jenkinsfile` to check out the triggered source and run `python -m unittest discover -s tests` after installing `requirements-dev.txt`; retain the existing lint stage (PBT-08).
8. [x] **Review isolation and source parity** — verify the P2 notebook selects `topics_by_project.P2` from the shared prod config; compare P2 notebook behavior with P1 after project-specific substitutions; confirm P2 table/checkpoint identifiers are unique; confirm no P1 files changed.
9. [x] **Update the design/implementation summary** — record created paths and any limits; update approved-plan checkboxes as each step is completed.

## Acceptance Checks

- P2 selects `my-test-p2` from the shared `prod` profile; P1 continues to use the unchanged default topic.
- P2 writes and checkpoints under P2-specific identifiers; the P2 job calls P2 notebooks.
- P1 notebooks and job remain unchanged; the shared production config retains the existing P1 topic and settings and adds only the P2 topic override.
- The Hypothesis property test exercises P2 topic override selection and `_jaas_quote` with generated inputs, deterministic generation, and shrinking.
- Jenkins installs Hypothesis through `requirements-dev.txt` and runs unittest discovery.
- No credentials or secret values are added.

## Testing to Run in Build & Test

- Black check and Ruff on changed Python files.
- `python -m unittest discover -s tests`.
- Static YAML validation and, if Databricks CLI is available, P2 bundle validation without deployment.
- Databricks/Kafka/Delta/S3 execution remains a separate environment-dependent check; do not claim it passed locally.
