# AI-DLC Intent Lifecycle

The project AI-DLC workflow is defined in `.agents/skills/aidlc-workflows/`. `aidlc-docs/aidlc-state.md` is the current intent state record; `aidlc-docs/audit.md` records active history. Closed intent summaries and full snapshots are stored in `aidlc-docs/archive/<intent-id>/`.

The lifecycle supports `ACTIVE`, `VERIFICATION_COMPLETE`, `VERIFICATION_WAIVED`, `COMPACTION`, `COMPACTION_FAILED`, `COMPACTED`, and `CLOSED`. `VERIFICATION_COMPLETE` requires successful Build and Test verification and approval. `VERIFICATION_WAIVED` requires explicit user acceptance of a documented limitation; it must never be reported as a passing result.

After a passed result or accepted waiver and separate approval to close, prepare a curated manifest at `aidlc-docs/compaction/<intent-id>/manifest.json`. A waiver manifest uses `verification.status: waived`, `verification.user_accepted: true`, and details describing the unverified scope; the lifecycle state must record the same accepted waiver. Run a dry-run and review its archive, canonical updates, and cleanup list before applying.

Use `python3 scripts/aidlc_intent.py compact <intent-id> --dry-run` to preview and `python3 scripts/aidlc_intent.py compact <intent-id> --apply` to archive the complete listed history, apply curated canonical updates, clear workflow-only inception/construction artifacts, and close the intent. Never put application source or configuration in cleanup paths. Runtime waivers do not authorize deployment.
