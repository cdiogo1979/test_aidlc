"""Property tests for P2 topic selection and Kafka JAAS escaping."""

from __future__ import annotations

import ast
import string
import unittest
from pathlib import Path
from typing import Any, Callable, cast

from hypothesis import given, settings, strategies as st


def _load_p2_helpers() -> tuple[Callable[..., str], Callable[[str], str]]:
    """Load pure helper functions from the P2 bronze notebook source.

    Returns:
        tuple: P2 project-topic resolver and JAAS escaping function.
    """
    notebook_path = Path(__file__).resolve().parents[1] / "notebooks" / "P2" / "bronze" / "bronze_ingestion.py"
    tree = ast.parse(notebook_path.read_text(encoding="utf-8"))
    required_names = {"_project_kafka_topic", "_jaas_quote"}
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in required_names]
    if {node.name for node in functions} != required_names:
        raise ValueError("Expected P2 topic and JAAS helpers were not found.")
    module = ast.Module(body=functions, type_ignores=[])
    namespace: dict[str, object] = {"Any": Any}
    exec(
        compile(ast.fix_missing_locations(module), str(notebook_path), "exec"),
        namespace,
    )
    return (
        cast(Callable[..., str], namespace["_project_kafka_topic"]),
        cast(Callable[[str], str], namespace["_jaas_quote"]),
    )


_project_kafka_topic, _jaas_quote = _load_p2_helpers()


class P2PipelinePropertyTests(unittest.TestCase):
    """Verify generated configuration and escaping invariants."""

    @settings(derandomize=True)
    @given(
        topic=st.text(
            alphabet=string.ascii_letters + string.digits + "-._",
            min_size=1,
        )
    )
    def test_selects_explicit_p2_topic_override(self, topic: str) -> None:
        """Choose P2's mapped topic and never use the shared default topic.

        Args:
            topic: Generated Kafka topic name assigned to P2.
        """
        kafka_config = {
            "topic": "p1-default-topic",
            "topics_by_project": {"P2": topic},
        }

        self.assertEqual(_project_kafka_topic(kafka_config, "P2"), topic)

    def test_missing_p2_override_fails_closed(self) -> None:
        """Reject missing P2 configuration instead of consuming P1's default."""
        with self.assertRaisesRegex(ValueError, "project 'P2'"):
            _project_kafka_topic({"topic": "p1-default-topic", "topics_by_project": {}}, "P2")

    @settings(derandomize=True)
    @given(
        prefix=st.text(),
        special=st.sampled_from(("\\", '"')),
        suffix=st.text(),
    )
    def test_escapes_quotes_and_backslashes_without_losing_text(self, prefix: str, special: str, suffix: str) -> None:
        """Escape JAAS metacharacters while preserving all source characters.

        Args:
            prefix: Arbitrary text before a required special character.
            special: A quote or backslash that must be escaped.
            suffix: Arbitrary text after the special character.
        """
        value = prefix + special + suffix
        expected = "".join({"\\": "\\\\", '"': '\\"'}.get(character, character) for character in value)

        self.assertEqual(_jaas_quote(value), expected)
