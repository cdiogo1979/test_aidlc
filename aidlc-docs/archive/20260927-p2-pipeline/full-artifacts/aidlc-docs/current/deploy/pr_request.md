# PR Request: Add P2 Kafka Pipeline

## Problem
Create a second daily Databricks pipeline that follows P1's processing behavior while consuming Kafka topic `my-test-p2` and keeping its persisted state isolated from P1.

## Solution
Add an independent P2 Databricks bundle and P2 bronze/silver notebooks. Keep the existing production config shared by all projects, retain `kafka.topic: my-topic` for P1, and add an explicit `kafka.topics_by_project.P2: my-test-p2` override. P2 fails closed if its project topic override is absent.

## Main Changes
- `configs/prod.yaml`: add the P2 topic mapping without changing P1's default topic or shared Kafka settings.
- `notebooks/P2/bronze/bronze_ingestion.py` and `notebooks/P2/silver/silver_processing.py`: add P2 processing with P2 tables/checkpoints and the existing six-cell notebook structure.
- `jobs/P2/databricks.yml` and `jobs/P2/resources/p2-daily-pipeline.yml`: add a separate P2 bundle/job with the P1 task order and scheduling controls.
- `tests/test_p2_pipeline_properties.py`: add deterministic Hypothesis properties for P2 topic selection and JAAS quoting.
- `requirements-dev.txt` and `cicd/Jenkinsfile`: add Hypothesis, Flake8, and Bandit; run Ruff, Flake8, and Bandit as parallel Code Analysis sub-stages; then run unittest discovery. The CI commands use the configured `venv` directly.

## Verification
- Ruff, Python syntax compilation, YAML parsing, and all 25 unit/property tests passed.
- Black formatting/check passed with Black 25.11.0 and the property suite passed with Hypothesis 6.141.1. These differ from the repository pins (26.5.1 and 6.168.1) because the configured package index did not offer the pinned releases.
- The local unit suite passed before the latest Jenkins Code Analysis additions. The Jenkins pipeline has not been run with its venv fix or parallel analyzers, so those pipeline stages remain unverified. The configured local package index lacks pinned Flake8 7.4.1, which prevented local execution of the new Code Analysis stage. The user explicitly accepted this additional verification limitation; Jenkins execution and the new analysis checks remain unverified.
- Databricks bundle validation and Databricks/Kafka/storage runtime execution were not performed; the Databricks CLI and workspace services were unavailable.
- The user approved Build & Test and explicitly accepted the documented external verification limitation by responding `**Approve & Continue**`. This is a verification waiver, not evidence of bundle validity or runtime success. Jenkins execution and the new Code Analysis stage also remain unverified.

## Deployment
Environment deployment and operational validation are required. Follow [deploy_instructions.md](deploy_instructions.md). Deployment is conditional on resolving the listed inputs and completing Databricks bundle validation. No PR has been created and no deployment has occurred.

## Risks and Limitations
- Bundle variable values, target workspace, identity, cluster policy, runtime, retry policy, and schedule must be supplied/confirmed by the deployment owner; they are not guessed here.
- The shared production config has null Kafka username and secret scope placeholders. Supply approved non-secret identifiers and configure the secret value in Databricks Secret Scope without putting credentials in source control.
- Kafka topic existence/permissions, storage/catalog locations, P2 table permissions, checkpoint access, job identity, and runtime compatibility require validation in the target workspace.
- No rollback procedure for a P2 job deployment or resulting P2 data/checkpoint state is defined in this intent. Confirm recovery/disablement ownership before enabling scheduled execution.
