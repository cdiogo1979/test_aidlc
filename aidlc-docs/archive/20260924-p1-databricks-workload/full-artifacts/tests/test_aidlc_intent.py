"""Behavioral tests for manifest-driven AI-DLC artifact compaction."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import aidlc_intent


class CompactionTests(unittest.TestCase):
    """Exercise compaction lifecycle behavior in isolated workspaces."""

    def setUp(self):
        """Create a temporary workspace with a verification-complete intent."""
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "aidlc-docs").mkdir()
        (self.root / "aidlc-docs/aidlc-state.md").write_text("# State\n", encoding="utf-8")
        (self.root / "aidlc-docs/audit.md").write_text("# Audit\nFull history\n", encoding="utf-8")
        (self.root / "aidlc-docs/construction/U1").mkdir(parents=True)
        (self.root / "aidlc-docs/construction/U1/design.md").write_text("workflow evidence", encoding="utf-8")
        aidlc_intent._write_lifecycle(self.root, {"intent_id": "20260924-example", "status": "VERIFICATION_COMPLETE"})
        self.manifest = {
            "intent_id": "20260924-example", "name": "Example", "objective": "Keep durable knowledge",
            "date": "2026-09-24", "scope": "One small unit", "workstreams": ["U1"],
            "verification": {"status": "passed", "details": "All checks passed"},
            "artifact_inventory_complete": True,
            "summary": {"major_requirements": ["Requirement A"], "design_decisions": ["Decision B"],
                        "implementation_decisions": ["Implementation C"], "deviations": [], "superseded_decisions": []},
            "canonical_updates": [{"path": "aidlc-docs/knowledge/decisions.md", "content": "# Decisions\nCurrent value = 90\n"}],
            "artifacts": ["aidlc-docs/construction/U1"],
            "cleanup_paths": ["aidlc-docs/construction/U1"],
        }

    def tearDown(self):
        """Remove the isolated temporary workspace."""
        self.temp.cleanup()

    def _lifecycle(self):
        """Return parsed lifecycle metadata from the test state file."""
        state = (self.root / aidlc_intent.STATE_FILE).read_text(encoding="utf-8")
        return aidlc_intent._load_lifecycle(state)[0]

    def test_completed_intent_compacts_and_closes(self):
        """A passed intent archives and closes only after successful compaction."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        state = (self.root / aidlc_intent.STATE_FILE).read_text(encoding="utf-8")
        self.assertEqual("CLOSED", self._lifecycle()["status"])
        self.assertEqual(1, state.count("## Intent Lifecycle"))

    def test_user_accepted_verification_waiver_compacts_with_waiver_recorded(self):
        """An explicitly accepted waiver may close without claiming tests passed."""
        aidlc_intent._write_lifecycle(self.root, {
            "intent_id": "20260924-example", "status": "VERIFICATION_WAIVED",
            "verification_outcome": "waived",
            "verification_waiver": {"accepted_by_user": True},
        })
        self.manifest["verification"] = {
            "status": "waived", "user_accepted": True,
            "details": "Runtime verification unavailable; limitation accepted by user.",
        }
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        summary = (self.root / "aidlc-docs/archive/20260924-example/intent-summary.md").read_text()
        self.assertIn("Runtime verification unavailable", summary)
        self.assertEqual("CLOSED", self._lifecycle()["status"])

    def test_verification_waiver_requires_explicit_user_acceptance(self):
        """A waiver manifest without explicit acceptance fails before filesystem changes."""
        self.manifest["verification"] = {
            "status": "waived", "user_accepted": False, "details": "Runtime unavailable.",
        }
        with self.assertRaises(aidlc_intent.CompactionError):
            aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertFalse((self.root / "aidlc-docs/archive").exists())

    def test_waived_lifecycle_requires_recorded_acceptance(self):
        """A waived lifecycle without recorded user acceptance cannot compact."""
        aidlc_intent._write_lifecycle(self.root, {
            "intent_id": "20260924-example", "status": "VERIFICATION_WAIVED",
            "verification_outcome": "waived",
        })
        self.manifest["verification"] = {
            "status": "waived", "user_accepted": True, "details": "Runtime unavailable.",
        }
        with self.assertRaises(aidlc_intent.CompactionError):
            aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertFalse((self.root / "aidlc-docs/archive").exists())

    def test_missing_canonical_document_is_created(self):
        """A canonical document is created from the curated replacement content."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertIn("Current value = 90", (self.root / "aidlc-docs/knowledge/decisions.md").read_text())

    def test_existing_canonical_document_is_updated_in_place(self):
        """Updating canonical content does not create a duplicate document."""
        target = self.root / "aidlc-docs/knowledge/decisions.md"
        target.parent.mkdir()
        target.write_text("Old value = 30\n", encoding="utf-8")
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertEqual("# Decisions\nCurrent value = 90\n", target.read_text())
        self.assertEqual([target], list(target.parent.glob("*.md")))

    def test_superseded_value_is_replaced_and_history_preserved(self):
        """Latest canonical values replace old values while old source evidence is archived."""
        (self.root / "aidlc-docs/construction/U1/decision.md").write_text("API timeout = 30 seconds", encoding="utf-8")
        self.manifest["artifacts"] = ["aidlc-docs/construction/U1"]
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        canonical = (self.root / "aidlc-docs/knowledge/decisions.md").read_text()
        historical = (self.root / "aidlc-docs/archive/20260924-example/full-artifacts/aidlc-docs/construction/U1/decision.md").read_text()
        self.assertIn("90", canonical)
        self.assertIn("30", historical)

    def test_workflow_artifacts_are_archived_then_removed(self):
        """Workflow artifacts remain in full archive after active cleanup."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertFalse((self.root / "aidlc-docs/construction/U1").exists())
        self.assertTrue((self.root / "aidlc-docs/archive/20260924-example/full-artifacts/aidlc-docs/construction/U1/design.md").exists())

    def test_full_audit_is_archived_and_active_audit_points_to_it(self):
        """The full audit snapshot survives while the active surface holds a pointer."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertIn("Full history", (self.root / "aidlc-docs/archive/20260924-example/full-artifacts/aidlc-docs/audit.md").read_text())
        self.assertIn("archive/20260924-example/full-artifacts/aidlc-docs/audit.md", (self.root / "aidlc-docs/audit.md").read_text())

    def test_intent_summary_is_generated(self):
        """The summary records key content and archive references."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        summary = (self.root / "aidlc-docs/archive/20260924-example/intent-summary.md").read_text()
        self.assertIn("Requirement A", summary)
        self.assertIn("Full artifacts and audit snapshot", summary)

    def test_second_apply_is_idempotent(self):
        """Repeating an identical apply leaves canonical and archive content unchanged."""
        aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        target = self.root / "aidlc-docs/knowledge/decisions.md"
        before = target.read_bytes()
        result = aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertIn("already CLOSED", result)
        self.assertEqual(before, target.read_bytes())

    def test_dry_run_does_not_modify_files(self):
        """Dry-run reports actions and leaves the workspace byte-for-byte untouched."""
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = aidlc_intent.compact(self.root, "20260924-example", self.manifest, dry_run=True)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertIn("Canonical documents to create/update", report)
        self.assertIn("Intent summary:", report)

    def test_failure_does_not_close_and_is_retryable(self):
        """A failed archive copy sets a retryable state, and successful retry can close."""
        with patch.object(aidlc_intent, "_copy_verified", side_effect=OSError("disk failure")):
            with self.assertRaises(aidlc_intent.CompactionError):
                aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertEqual("COMPACTION_FAILED", self._lifecycle()["status"])
        with patch.object(aidlc_intent, "_copy_verified", wraps=aidlc_intent._copy_verified):
            aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertEqual("CLOSED", self._lifecycle()["status"])

    def test_context_selection_excludes_archive(self):
        """Default context includes current state and canonical docs, never archives."""
        (self.root / "aidlc-docs/knowledge").mkdir()
        (self.root / "aidlc-docs/knowledge/current.md").touch()
        (self.root / "aidlc-docs/archive/old").mkdir(parents=True)
        (self.root / "aidlc-docs/archive/old/intent-summary.md").touch()
        paths = aidlc_intent.active_context_paths(self.root)
        self.assertIn("aidlc-docs/knowledge/current.md", paths)
        self.assertFalse(any("archive" in path for path in paths))

    def test_legacy_state_is_left_unchanged(self):
        """A legacy state without lifecycle metadata keeps its existing stage workflow."""
        (self.root / aidlc_intent.STATE_FILE).write_text("# Legacy stage state\n", encoding="utf-8")
        with self.assertRaises(aidlc_intent.CompactionError):
            aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertEqual("# Legacy stage state\n", (self.root / aidlc_intent.STATE_FILE).read_text())

    def test_unverified_intent_cannot_compact(self):
        """The manifest verification gate rejects work before archive mutation."""
        self.manifest["verification"]["status"] = "failed"
        with self.assertRaises(aidlc_intent.CompactionError):
            aidlc_intent.compact(self.root, "20260924-example", self.manifest)
        self.assertFalse((self.root / "aidlc-docs/archive").exists())


if __name__ == "__main__":
    unittest.main()
