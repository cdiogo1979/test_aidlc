# PR Request: Python build quality and canonical design guidance

## Problem

The project lacked prescribed Python formatting and linting checks, and AI-DLC had no consistent convention for maintaining canonical subproject and component design knowledge.

## Solution

Added reproducible Black and Ruff configuration and dependencies, updated developer and AI-DLC workflow guidance, and curated canonical P1 design summaries from approved historical artifacts.

## Main changes

- Added `pyproject.toml` and `requirements-dev.txt` for Black and Ruff.
- Updated `.agents/skills/aidlc-workflows/` and `AGENTS.md` with format/lint and canonical design guidance.
- Added P1 application and functional design knowledge under `aidlc-docs/knowledge/P1/`.

## Verification

Static review only. Python tools and runtime tests were not run, per the approved execution plan. Verification has not passed; the intent requires explicit acceptance of this limitation before closure.

## Deployment

No environment deployment or operational steps are required. The changes affect repository developer guidance and configuration only.

## Risks and limitations

Black and Ruff behavior, and Databricks runtime behavior, remain unverified. P1 runtime behavior was not tested. Review the tool configuration and run the repository Build & Test steps before relying on those checks in CI or production workflows.
