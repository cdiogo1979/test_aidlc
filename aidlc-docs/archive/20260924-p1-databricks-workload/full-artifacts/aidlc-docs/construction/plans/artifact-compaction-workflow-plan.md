# AI-DLC Artifact Compaction / Intent Closure — Implementation Plan

## Inspection findings

- AI-DLC is implemented as an instruction-driven skill in `.agents/skills/aidlc-workflows/`; there is no runtime workflow engine or intent state-machine code.
- `aidlc-docs/aidlc-state.md` is the single project/stage state record. Stage progress uses Markdown checkboxes and there is no intent ID or close status.
- Workflow artifacts are written to `aidlc-docs/inception/` and `aidlc-docs/construction/`; full interaction history is appended to `aidlc-docs/audit.md`.
- No canonical knowledge area, intent archive convention, compaction command, or tests exist.
- Git has a single checked-out `master` branch and no workflow-specific branch/worktree/merge process. The repository's current tracked baseline contains only `README.md`; workflow and project files are presently untracked. This proposal adds no branch or merge behavior.
- Existing `aidlc-docs/` files are one active P1 workflow. Runtime verification has not run; a user-approved limitation waiver is recorded. They will not be compacted without explicit closure approval.

## Proposed implementation

Use the current Markdown workflow as the lifecycle authority, and add a small standard-library compaction utility only for deterministic file/state operations. The utility will not infer or blindly copy canonical knowledge: the AI-DLC workflow must curate canonical updates and produce an explicit manifest before applying compaction.

### Active and historical locations

- Keep the current inception/construction artifact locations while an intent is active.
- Add `aidlc-docs/knowledge/` for concise, current canonical project documents. Update an existing canonical document in place; do not create duplicate documents for the same topic.
- Add `aidlc-docs/archive/<intent-id>/intent-summary.md` and `full-artifacts/` for each closed intent. Preserve the complete intent artifact set and an audit snapshot there.
- Keep the active `aidlc-docs/aidlc-state.md` as the one state record. After closure, it points to the archived summary and records the closed lifecycle status. A later intent reuses the same state file; the archived state snapshot preserves prior state.
- After compaction, the active `audit.md` contains the current/new intent's entries and an archive pointer; the complete prior audit remains in that intent's archive.

### State and lifecycle

Extend the existing state file with a stable intent ID and lifecycle status:

`ACTIVE -> VERIFICATION_COMPLETE | VERIFICATION_WAIVED -> COMPACTION -> COMPACTED -> CLOSED`

Add `COMPACTION_FAILED` as a recoverable error state. Assign IDs as `YYYYMMDD-<intent-slug>` at intent start, adding a numeric suffix only to resolve a collision, and persist them in the same `aidlc-state.md`; do not create a second state machine or database. Adopt `20260924-p1-databricks-workload` for the current P1 intent without changing its U3 approval gate or compacting it. Only successful Build and Test verification can enter `VERIFICATION_COMPLETE`; an explicit user-approved limitation may enter `VERIFICATION_WAIVED`, which never asserts checks passed. The intent is not `CLOSED` until canonical updates, summary, archive, and active-surface cleanup are all confirmed.

### Compaction workflow

After successful verification or an explicit user-approved verification waiver, and after separate closure approval:

1. Analyze the completed intent's requirements, decisions, designs, implementation constraints, verification results, and audit history.
2. Classify each artifact as canonical knowledge, workflow-specific, or audit/history.
3. Curate and update canonical documents under `aidlc-docs/knowledge/`; reconcile superseded decisions so only the latest valid decision is active.
4. Create an explicit compaction manifest that lists canonical updates (including the complete curated replacement content and prior canonical versions to preserve) and every artifact to archive. Include a compact `intent-summary.md` with intent ID/name, objective, date, scope, units/workstreams, major requirements and decisions, implementation decisions, deviations, verification result, canonical documents updated, superseded decisions, and archive references.
5. Run a dry-run preview listing canonical create/update operations, archive paths, retained history, and the summary path.
6. On apply, snapshot all listed artifacts and the full audit to a staging archive, verify the staged content, then finalize the archive and clear intent-specific workflow artifacts from the active inception/construction surface. Keep source code/configuration that remains the current product implementation in its existing application locations; include its intent snapshot in the archive when modified by the intent.
7. Mark `COMPACTED`, then `CLOSED`, only after archive and cleanup verification succeeds. On any failure, preserve the archive/source material, set `COMPACTION_FAILED`, and permit safe retry.

### Command and idempotence

There is no existing CLI to extend. Add a narrowly scoped command:

```bash
python scripts/aidlc_intent.py compact <intent-id> --dry-run
python scripts/aidlc_intent.py compact <intent-id> --apply
```

Dry-run is read-only. Apply consumes a manifest produced by the compaction workflow. Use stable IDs, deterministic archive paths, content verification, and no-op behavior for an already closed intent so repeated compaction does not duplicate or corrupt canonical documentation. The tool fails closed if the intent is not verification-complete/compacting or the manifest is incomplete.

Future workflow context loading uses canonical knowledge and the current active intent/state only. It must not glob, enumerate, or automatically ingest every archive. Historical intent summaries and full artifacts are retrieved selectively when relevant.

## Files proposed for change

- `.agents/skills/aidlc-workflows/SKILL.md` — lifecycle integration and transition rules.
- `.agents/skills/aidlc-workflows/references/common/artifact-compaction.md` — classification, manifest, dry-run/apply, idempotence, failure recovery, archive, and summary procedures.
- `.agents/skills/aidlc-workflows/references/common/process-overview.md` and `terminology.md` — lifecycle stage and canonical/history vocabulary.
- `.agents/skills/aidlc-workflows/references/common/session-continuity.md` — load canonical/current context by default and retrieve archives selectively.
- `.agents/skills/aidlc-workflows/references/construction/build-and-test.md` — set `VERIFICATION_COMPLETE` only after successful verification and approval; transition to compaction.
- `scripts/aidlc_intent.py` — manifest-driven dry-run/apply utility.
- `tests/test_aidlc_intent.py` — standard-library automated tests.
- `.gitignore` — only if test/runtime cache artifacts require it.

The shared rule files will stay project-neutral. No current P1 workflow artifacts will be moved or compacted until the user separately approves closure.

### User-approved verification waiver extension (2026-09-24)

Because no Databricks environment is available for P1, the user selected an explicit limitation waiver path. The lifecycle and compaction utility now support `VERIFICATION_WAIVED` with a manifest outcome of `waived`, explicit user acceptance, and explanatory details. The P1 runtime checks remain unverified. Compaction still requires separate user approval and does not authorize deployment.

## Automated test coverage

Use Python `unittest` and isolated temporary workspaces to cover:

1. A verification-complete intent compacts successfully.
2. Missing canonical documents are created.
3. Existing canonical documents are updated in place, without duplicate files.
4. A newer canonical decision replaces the old active value while the old artifact remains archived.
5. Workflow-only artifacts are removed from the active surface and preserved in the archive.
6. The complete audit remains available in the archive and the active audit points to it.
7. The intent summary is generated at its stable archive path.
8. Repeating the same apply is idempotent.
9. Dry-run changes no files or state.
10. An injected apply failure never leaves the intent marked `CLOSED` and remains recoverable.
11. New-intent context selection returns canonical/current state paths and does not include archived intent paths by default.
12. Legacy/in-progress state and workflows without compaction metadata continue normal stage processing.

## Verification and completion

- Run `python -m unittest discover -s tests -v` after implementation.
- Check the shared workflow files for project-specific identifiers and stale lifecycle descriptions.
- Inspect dry-run and applied archive trees in temporary fixtures; do not compact the active P1 project during implementation tests.
- Preserve the current Git branch/worktree behavior; no commits, branch changes, or merges are part of the feature.

## Plan status

- [x] Inspect current workflow, state, artifacts, Git behavior, commands, and tests.
- [x] Propose the smallest coherent design compatible with the instruction-based workflow.
- [x] User approves this implementation plan (`Approve & continue`, 2026-09-24).
- [x] Implement lifecycle and artifact-compaction workflow documentation.
- [x] Implement manifest-driven, dry-run/idempotent compaction utility.
- [x] Add and run the lifecycle utility tests (16 tests currently pass, including verification-waiver acceptance and rejection coverage).
- [x] Perform documentation consistency sweep and present results.
