# Project guide for agents

## Purpose

This repository is used to build and maintain Databricks artifacts. Keep generated and hand-maintained artifacts organized by their role and environment.

## Repository structure

- `configs/`: environment-specific configuration for Databricks deployments and jobs. Keep environment-dependent values here instead of hard-coding them in notebooks or job definitions. Do not commit secrets; use the project's approved secret store or secret references.
- `notebooks/<project>/`: Python Databricks notebook source files, grouped by subproject. Each subproject may contain `bronze/`, `silver/`, and `gold/` folders for medallion-layer notebooks, plus `ops/` and `deploy/` folders for operational and asset-deployment notebooks.
- `jobs/<project>/`: The single source of truth for Databricks jobs for the matching subproject. A job may be defined as Jobs API JSON or as a Databricks Declarative Automation Bundle (`databricks.yml` plus included resource YAML). Use bundle variables/targets when deployment supplies environment-specific values; do not keep duplicate JSON and bundle definitions for the same job.
- `aidlc-docs/current/`: Active AI-DLC intent documents, stage artifacts, `aidlc-state.md`, and `audit.md`. Keep current workflow material here until intent closure.
- `aidlc-docs/knowledge/`: Canonical, current project facts that should carry across intents.
- `aidlc-docs/knowledge/<project>/application-design.md`: The canonical application architecture for a Databricks subproject.
- `aidlc-docs/knowledge/<project>/functional-design/<component>.md`: One canonical functional-design document per component/unit, consolidating business logic, rules, and domain entities.
- `aidlc-docs/archive/<intent-id>/`: Immutable snapshots and summaries for closed intents. Do not edit archived history.
- `.agents/skills/aidlc-workflows/`: AI-DLC software development workflow. Follow its `SKILL.md` and referenced rules for software development work.

## Subproject layout

Create a matching subfolder under both `notebooks/` and `jobs/` for every new subproject. Use the subproject's name consistently in both locations. For example, subproject `P1` uses:

```text
notebooks/
└── P1/
    ├── bronze/
    ├── silver/
    ├── gold/
    ├── ops/
    └── deploy/
jobs/
└── P1/
```

Place each Python notebook in the layer folder that matches its role: `bronze/` for raw ingestion, `silver/` for cleaned or conformed data, and `gold/` for curated, consumption-ready data. Put the subproject's authoritative Databricks job definition in `jobs/<project>/`. When using a bundle, keep its `databricks.yml` at that folder's root and included job resources in a subfolder such as `resources/`.

The `ops/` and `deploy/` folders hold two additional notebook types:

- `ops/`: operational scripts run as needed for tasks such as data migrations, data patching, or other maintenance. These are not medallion pipeline notebooks; document any prerequisites and execution considerations in the notebook's Information cell.
- `deploy/`: notebooks that deploy or update Databricks assets not created by the data pipelines, such as views. Keep these separate from pipeline processing and describe the target assets and deployment assumptions in the notebook's Information cell.

## Expected artifacts

When adding or changing a Databricks workload, update the relevant artifacts together:

1. Python notebook source in `notebooks/<project>/<layer>/` for the workload logic.
2. A Databricks job definition in `jobs/<project>/` when the workload is scheduled or orchestrated. Use Jobs API JSON or a Declarative Automation Bundle YAML definition, according to the approved deployment approach.
3. Configuration in `configs/` for values that vary by environment.

Use descriptive, consistent names so that job definitions clearly identify the notebooks and configuration they use. Keep environment-specific settings out of shared notebook logic where practical.

## Working conventions

- Inspect the existing files and naming patterns before introducing new artifact formats or directories.
- Structure each Databricks notebook as six ordered cells: **Information**, **Imports**, **Widgets**, **Parameters**, **Additional Functions**, and **Main Execution**. Keep each section in its own notebook cell, in that order; omit a section only when it is not applicable.
- Whenever a notebook is changed, revise its opening Information comments so they accurately describe its current purpose, behavior, inputs, and material operational effects.
- Include a Google-style docstring on every generated function, including methods. Document arguments, return values, and raised exceptions when applicable; omit sections that do not apply.
- Format changed Python files with Black and lint them with Ruff as part of Build & Test. Use the versions and settings declared in `requirements-dev.txt` and `pyproject.toml`; report both results in the Build & Test summary.
- Keep job JSON valid or bundle configuration valid, and ensure notebook paths and parameters refer to repository artifacts that exist.
- Keep durable design knowledge under `aidlc-docs/knowledge/<project>/`: one application design per subproject and one consolidated functional design per component. Keep drafts and approval artifacts under `aidlc-docs/current/`; promote approved design decisions during intent closure and retain originals in the archive.
- Make configuration differences explicit by environment; do not silently apply one environment's settings to another.
- Do not put credentials, tokens, or other secrets in notebooks, job JSON, bundle YAML, or checked-in configuration.
- Update this guide when the repository structure or artifact conventions change.
