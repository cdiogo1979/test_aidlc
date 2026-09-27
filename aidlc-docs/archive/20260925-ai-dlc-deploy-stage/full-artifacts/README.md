# test_aidlc

## AI-DLC documentation

Keep workflow documents grouped by lifecycle:

```text
- `aidlc-docs/current/`: Open intent documents, stage artifacts, manifests, state, and audit.
- `aidlc-docs/knowledge/`: Canonical project facts carried across intents.
- `aidlc-docs/archive/<intent-id>/`: Closed intent summary and full artifact snapshot.
```

Compaction archives the current intent's documents before clearing its workflow-only files. The current state and audit remain as the active lifecycle record and archive pointer. Do not edit closed snapshots under `archive/`.
