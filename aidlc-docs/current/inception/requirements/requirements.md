# Requirements: Python Formatting and Linting in Build & Test

## Intent

Improve AI-DLC developer guidance by adding Python formatting/linting to Build & Test and maintaining canonical subproject design knowledge.

## Requirements

1. Provide a reproducible development dependency declaration for Black and Ruff.
2. Configure both tools for the repository's Python 3.11 Databricks code, with an 88-character line length.
3. Ensure Ruff recognizes Databricks-provided `spark` and `dbutils` names and accommodates the notebook import bootstrap pattern.
4. Update Build & Test instructions to format changed Python files, run a non-mutating Black check, and lint those files with Ruff.
5. Include formatter and linter results in generated Build & Test summaries.
6. Maintain one canonical application-design Markdown document per subproject under `aidlc-docs/knowledge/<project>/`.
7. Maintain one consolidated canonical functional-design Markdown document per component under `aidlc-docs/knowledge/<project>/functional-design/`, combining business logic, rules, entities/relationships, and relevant failure behavior.
8. Keep in-progress designs and approval artifacts in `aidlc-docs/current/`; promote curated approved design updates only during authorized intent closure, preserving historical originals in the archive.
9. Load a subproject's canonical application design and only affected component functional designs as context for new or resumed work.
10. Seed P1 canonical design knowledge from its existing archived approved designs without modifying the archives or implying runtime verification.

## Scope and Constraints

- This is an internal developer-tooling and workflow change; user stories and infrastructure design are not applicable.
- The workflow guidance should prefer changed Python paths to avoid unrelated repository-wide reformatting.
- Do not execute formatter, linter, or tests as part of this change unless separately requested.
