# Execution Plan: AI-DLC Developer Workflow Enhancements

## Approach

1. Add pinned Black and Ruff development dependencies and shared repository configuration; update Build & Test and `AGENTS.md` with the Python quality checks.
2. Define canonical per-subproject application-design and per-component functional-design locations in the skill, `AGENTS.md`, and lifecycle knowledge.
3. Update Application Design and Functional Design to consume canonical baselines while preserving active review artifacts in `current/`.
4. Update compaction rules to consolidate approved current design into one subproject application design and one functional design per affected component.
5. Update session continuity to load only the relevant subproject and component knowledge.
6. Create P1 canonical design summaries from approved archived design artifacts, without modifying archives or claiming runtime verification.
7. Review the resulting docs and links for consistency. Do not run tests or tools in this change.

## Acceptance Criteria

- Black and Ruff versions are explicit and reproducible.
- Black and Ruff share the 88-character line length and Python 3.11 target.
- Ruff handles Databricks notebook builtins and the current notebook import-bootstrap pattern.
- Build & Test guidance documents install, format, check, lint, and reporting commands.
- No existing notebooks are reformatted as a side effect.
- Each P1 subproject has one canonical application-design document and each of U1–U4 has one consolidated canonical functional-design document.
- Historical archive content remains unchanged, and P1 runtime verification limitations remain explicit.
