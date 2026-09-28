# Intent Summary: P2 Kafka Pipeline

## Intent
P2 Kafka Pipeline (`20260927-p2-pipeline`)

## Objective
Add a P2 daily Databricks pipeline equivalent to P1 processing with a separate Kafka topic and isolated state.

## Date
2026-09-27

## Scope
P2 shared-config topic override, bronze/silver notebooks, isolated job bundle and state, property tests, Jenkins CI analysis/test steps, and AI-DLC artifacts. Deployment and runtime execution are excluded.

## Units / workstreams
P2 Bronze Ingestion, P2 Silver Processing and Quarantine, P2 Daily Job, Shared Production Configuration, CI Code Analysis and Property Tests

## Major requirements
- P2 duplicates P1 bronze/silver daily processing semantics while consuming only Kafka topic my-test-p2.
- Use shared configs/prod.yaml for all projects; preserve P1 kafka.topic and select P2 through topics_by_project.P2.
- Isolate P2 tables, quarantine output, checkpoints, notebooks, and job resources from P1.
- Add deterministic Hypothesis properties and CI Code Analysis/test stages.

## Architecture and design decisions
- P2 topic selection requires an explicit project override and does not fall back to the P1 default.
- The P2 job runs bronze before silver; bronze Delta/CDF remains their data handoff.
- P2 follows P1 deployment inputs and runtime requirement; schedule, identity, compute, and retry values remain deployment-provided.

## Implementation decisions
- Created P2 bronze and silver notebooks with P2-specific table and checkpoint identifiers.
- Created an independent Databricks bundle and daily job under jobs/P2.
- Added P2 topic mapping to shared production config without changing P1 default.
- Added Hypothesis tests, pinned Flake8/Bandit dependencies, and parallel Ruff Lint, Flake8 Style Check, and Bandit Security Scan Jenkins sub-stages.
- Jenkins invokes Python, pip, Ruff, Flake8, and Bandit from the configured virtual environment directly.

## Deviations
- The initial separate P2 config/profile proposal was superseded after the user clarified that prod config is shared across projects.
- Local tools used Black 25.11.0 and Hypothesis 6.141.1 instead of repository pins because the configured index lacked those pinned releases.
- Databricks bundle/runtime verification and the final Jenkins pipeline/analyzer run remain unverified under explicitly accepted limitations.

## Verification
Local checks passed for the code-generation result: Black 25.11.0, Ruff 0.16.6, Python syntax compilation, YAML parsing, and 25 unit/property tests using Hypothesis 6.141.1. Repository pins Black 26.5.1 and Hypothesis 6.168.1 were unavailable from the configured package index. Databricks bundle validation and Databricks/Kafka/Delta/storage runtime execution were not performed. After those checks, Jenkins was updated to use its venv consistently and to run Ruff, Flake8, and Bandit as parallel Code Analysis stages; the Jenkins pipeline and new analyzers were not executed. The configured package index did not provide pinned Flake8 7.4.1 (available through 7.3.0), preventing local analyzer execution. The user explicitly accepted both the external Databricks verification limitation and this additional Jenkins/analyzer limitation. No PR or deployment occurred.

## Canonical documents updated
- aidlc-docs/knowledge/P1/application-design.md
- aidlc-docs/knowledge/P2/application-design.md
- aidlc-docs/knowledge/P2/functional-design/U1-bronze-ingestion.md
- aidlc-docs/knowledge/P2/functional-design/U2-silver-processing-and-quarantine.md
- aidlc-docs/knowledge/P2/functional-design/U3-p2-integration.md

## Superseded decisions
- Separate configs/p2_prod.yaml and p2_prod profile were superseded by shared configs/prod.yaml and explicit topics_by_project.P2 override.

## Archived artifacts
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/aidlc-docs/current/inception
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/aidlc-docs/current/construction
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/aidlc-docs/current/deploy
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/configs/prod.yaml
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/jobs/P2
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/notebooks/P2
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/tests/test_p2_pipeline_properties.py
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/requirements-dev.txt
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/cicd/Jenkinsfile
- aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/aidlc-docs/current/compaction/20260927-p2-pipeline/manifest.json

## Archive
- Full artifacts and audit snapshot: `aidlc-docs/archive/20260927-p2-pipeline/full-artifacts/`
