# Build Instructions

## Build model

This repository has no Python package build or compiled application artifact. The deployable P1 artifact is the Declarative Automation Bundle under `jobs/P1/`; the notebook and shared library sources remain in the repository. Build verification consists of Python syntax checks and Databricks Bundle validation.

## Prerequisites

- Python 3.9 or later for the existing standard-library `unittest` suite and source syntax check.
- PyYAML available to the runtime because `src/common.py` imports `yaml` to read environment configuration.
- A Databricks Runtime 15.4 LTS or later with Delta VARIANT support for notebook execution.
- A Databricks CLI version supporting Declarative Automation Bundles, plus CLI authentication to the target workspace, for Bundle validation and deployment.
- Values for the required `prod` Bundle variables. The repository intentionally does not supply workspace-specific production values.

Spark and Delta dependencies are supplied by the Databricks Runtime. No local PySpark dependency file or Python package metadata is currently present.

## Environment inputs

Supply the variables listed in `aidlc-docs/construction/u3-p1-integration/code/code-summary.md` through approved `BUNDLE_VAR_*` environment variables or `jobs/P1/.databricks/bundle/prod/variable-overrides.json`. The `.databricks/` directory is ignored by Git and Bundle sync. Configure workspace authentication using the team's approved Databricks CLI profile or credential mechanism. Do not place passwords, tokens, or other secret values in the Bundle variables file.

## Build and validation steps

### 1. Check Python source syntax

From the repository root:

```bash
python3 -B -c 'from pathlib import Path; files = [Path("src/common.py"), *Path("notebooks/P1").rglob("*.py")]; [compile(p.read_text(encoding="utf-8"), str(p), "exec") for p in files]; print(f"Syntax OK for {len(files)} Python files")'
```

### 2. Validate the Bundle

After installing/configuring the approved Databricks CLI, supplying required variables, and setting up workspace authentication:

```bash
cd jobs/P1
databricks bundle validate -t prod
```

Validation must confirm the bundle resource and source paths resolve and that the runtime, schedule, cluster policy, run identity, and retry values satisfy the deployment contract. This command validates configuration; it does not deploy or run the job.

### 3. Deploy only through the approved release process

```bash
databricks bundle deploy -t prod
```

Deployment is outside local build verification. Do not deploy the `prod` target as a test. No deployment was performed during this Build and Test work.

## Expected result

No compiled artifact is produced. Successful local validation reports valid Python syntax and a valid Bundle configuration. The Databricks CLI Bundle validation has not been run in this workspace because the CLI and required deployment values/authentication are unavailable.

## Troubleshooting

- **Bundle reports a missing variable**: supply the required deployment variable through the approved target mechanism; do not invent or commit a production value.
- **Notebook path cannot be resolved**: run the Bundle command from `jobs/P1/` and confirm the selected sync paths and relative notebook path in `resources/p1-daily-pipeline.yml`.
- **Cluster policy rejects the job cluster**: obtain the approved P1 policy defaults and a compatible Databricks Runtime from the deployment owner.
- **Notebook cannot load YAML configuration**: ensure PyYAML is available to the selected Databricks Runtime and that the Bundle sync preserves `configs/` and `src/` beside `notebooks/P1/` in the deployed project layout.
- **Runtime rejects Delta VARIANT operations**: select a supported Databricks Runtime 15.4 LTS or later and confirm Delta VARIANT support is enabled for the silver table.
