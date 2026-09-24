# Artifact Compaction / Intent Closure

## Purpose and artifact meaning

Compaction is the final step after the existing workflow and either successful Build and Test verification or an explicit user-approved verification waiver. It reduces active context while preserving the historical record. A waiver records accepted risk; it must never be described as passed verification.

- **Canonical project knowledge** in `aidlc-docs/knowledge/` is the current authoritative project state.
- **Active workflow artifacts** in `aidlc-docs/inception/` and `aidlc-docs/construction/` support the current intent.
- **Temporary analysis** is not promoted to canonical knowledge; retain it in the archive when it is part of the intent record.
- **Intent summary** is a concise retrieval aid for a closed intent.
- **Intent archive** under `aidlc-docs/archive/<intent-id>/` contains the complete artifact snapshot and audit.
- **Audit** is detailed traceability. The full audit is archived at closure; the active audit becomes a pointer for subsequent history.

Historical artifacts are evidence of what happened. Canonical documents represent what is currently true. Do not blindly copy workflow artifacts into canonical documentation. Update an existing canonical topic in place. When decisions are superseded, keep only the latest valid value active and preserve earlier values in historical evidence and the summary's superseded-decisions section.

```text
Created → Used during workflow → Verified → Compacted
                                      ├─ Canonical knowledge → active project documentation
                                      ├─ Intent summary → compact historical context
                                      └─ Full artifacts → intent archive
```

## Lifecycle state

Use the existing `aidlc-docs/aidlc-state.md` as the single state record. Its machine-readable `Intent Lifecycle` JSON block is delimited by `<!-- intent-lifecycle:start -->` and `<!-- intent-lifecycle:end -->`.

`ACTIVE → VERIFICATION_COMPLETE | VERIFICATION_WAIVED → COMPACTION → COMPACTED → CLOSED`; failures use `COMPACTION_FAILED` and can retry. Use stable IDs `YYYYMMDD-<intent-slug>` with a numeric collision suffix if needed. Set `VERIFICATION_COMPLETE` only after successful Build and Test verification and approval. Set `VERIFICATION_WAIVED` only after the user explicitly accepts a specific, documented verification limitation; retain the limitation and unverified scope in state, audit, and summary. A waiver does not assert that verification passed. The current intent cannot be compacted while a stage approval gate is pending. Legacy projects without the block continue existing stage behavior and are ineligible for compaction until initialized.

## Prepare a curated manifest

After verification or explicit waiver, and after the user approves closure, create `aidlc-docs/compaction/<intent-id>/manifest.json`. For passed verification set `verification.status` to `passed`; for an accepted limitation set it to `waived`, include `user_accepted: true`, and describe the limitation in `details`. The manifest outcome must match lifecycle metadata. The AI-DLC author curates all canonical content and enumerates every artifact to preserve and every workflow-only path to clear. `artifact_inventory_complete` asserts the archive list is complete. This utility never infers durable knowledge from artifacts.

```json
{
  "intent_id": "20260924-example",
  "name": "Example intent",
  "objective": "What this intent delivered",
  "date": "2026-09-24",
  "scope": "Included and excluded scope",
  "workstreams": ["Unit 1"],
  "verification": {"status": "passed", "details": "Build and Test summary reference and result"},
  "artifact_inventory_complete": true,
  "summary": {
    "major_requirements": ["..."],
    "design_decisions": ["..."],
    "implementation_decisions": ["..."],
    "deviations": ["..."],
    "superseded_decisions": ["Old value replaced by new value; see archive evidence"]
  },
  "canonical_updates": [
    {"path": "aidlc-docs/knowledge/architecture.md", "content": "Complete curated replacement document content.\n"}
  ],
  "artifacts": ["aidlc-docs/inception/requirements/requirements.md", "aidlc-docs/construction/unit-1"],
  "cleanup_paths": ["aidlc-docs/inception/requirements", "aidlc-docs/construction/unit-1"]
}
```

Include source/config artifacts changed by the intent in `artifacts` when useful, but never put application code or configuration in `cleanup_paths`. The tool snapshots the complete state and audit too. Cleanup cannot target knowledge, archive, state, or audit. Paths must remain inside the workspace.

## Preview and apply

```bash
python scripts/aidlc_intent.py compact <intent-id> --dry-run
python scripts/aidlc_intent.py compact <intent-id> --apply
```

The default manifest path is `aidlc-docs/compaction/<intent-id>/manifest.json`; `--manifest` and `--root` override locations. Review the dry-run canonical create/update operations, archive inputs, active removals, audit retention, and summary path. Dry-run is read-only. Apply stages and verifies all listed artifacts, state, and complete audit before canonical updates or active cleanup. It then leaves an active audit pointer and records archive/summary references in state.

Archive paths are stable. An identical apply to a closed intent is a no-op; a conflicting manifest fails closed. Failures remain retryable and never report `CLOSED`. Protect partial archive material until checked against intact source artifacts.

## Future context loading

Load `aidlc-state.md`, canonical knowledge, and current active workflow artifacts. Never enumerate or automatically ingest `aidlc-docs/archive/`. Retrieve one summary or archived artifact only when its history is relevant. `active_context_paths()` in `scripts/aidlc_intent.py` demonstrates the default selector behavior.

## Completion checklist

- Verification passed and approval is recorded, or the user-approved verification waiver and its limits are recorded.
- Canonical content, summary, archive inventory, and cleanup paths are curated and complete.
- Dry-run was reviewed and made no changes.
- Apply finished; archived audit and artifacts are available; canonical decisions are current; only workflow artifacts were removed.
- State is `CLOSED`, with resolvable archive and summary references.
- Record closure in the active audit after its original full contents have been archived; never rewrite archived history.
