# Intent Summary: Python build quality and canonical design knowledge

## Intent
Python build quality and canonical design knowledge (`20260925-python-build-quality-tools`)

## Objective
Add reproducible Python formatting and linting guidance and establish canonical subproject and component design knowledge conventions.

## Date
2026-09-27

## Scope
Developer workflow tooling and documentation, Black/Ruff configuration, AI-DLC guidance, and curated P1 canonical design summaries; no Python or Databricks runtime execution.

## Units / workstreams
Python quality tooling, AI-DLC workflow guidance, P1 canonical design knowledge

## Major requirements
- Declare reproducible Black and Ruff developer tools and configure them for the repository.
- Document formatter and linter checks in the AI-DLC Build & Test workflow.
- Maintain one canonical application-design document per subproject and consolidated functional-design documents per component.
- Seed P1 canonical design summaries from approved prior artifacts without modifying historical archives.

## Architecture and design decisions
- Canonical application design is maintained under aidlc-docs/knowledge/<project>/.
- Canonical functional design is maintained per component under aidlc-docs/knowledge/<project>/functional-design/.
- Keep active workflow artifacts under aidlc-docs/current and preserve historical records in the intent archive.

## Implementation decisions
- Black and Ruff configuration and pinned development dependencies are stored in pyproject.toml and requirements-dev.txt.
- AI-DLC guidance and repository conventions are documented in the workflow skill and AGENTS.md.
- P1 canonical design documents were curated from approved historical artifacts.

## Deviations
- No formatter, linter, Python test, or Databricks runtime validation was run; the user accepted this explicit verification waiver.

## Verification
Explicitly accepted by the user: Black, Ruff, Python tests, and Databricks runtime validation were not run. Only static review was performed; verification is not passed.

## Canonical documents updated
- None recorded

## Superseded decisions
- None recorded

## Archived artifacts
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/current/inception
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/current/deploy
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/current/compaction/20260925-python-build-quality-tools/manifest.json
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/.agents/skills/aidlc-workflows
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/AGENTS.md
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/README.md
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/pyproject.toml
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/requirements-dev.txt
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/knowledge/P1
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/knowledge/aidlc-intent-lifecycle.md
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/aidlc-docs/knowledge/p1-databricks-workload.md
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/scripts/aidlc_intent.py
- aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/tests/test_aidlc_intent.py

## Archive
- Full artifacts and audit snapshot: `aidlc-docs/archive/20260925-python-build-quality-tools/full-artifacts/`
