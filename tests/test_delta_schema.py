"""Unit tests for additive P1 Delta schema migration helpers."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from typing import Any

from src.delta_schema import ensure_nullable_timestamp_column


class _FakeSparkType:
    """Minimal Spark data type double used by the schema helper tests."""

    def __init__(self, type_name: str) -> None:
        """Initialize a fake Spark type.

        Args:
            type_name: Spark SQL simple type name to expose.
        """
        self._type_name = type_name

    def simpleString(self) -> str:
        """Return this fake type's Spark SQL simple representation.

        Returns:
            str: The configured type name.
        """
        return self._type_name


class _FakeSparkSession:
    """Small SparkSession double that applies ADD COLUMNS statements."""

    def __init__(self, fields: list[Any] | None = None) -> None:
        """Initialize the fake session with an initial schema.

        Args:
            fields: Existing schema fields, if any.
        """
        self.fields = list(fields or [])
        self.statements: list[str] = []
        self.fail_inspection = False
        self.fail_migration = False
        self.omit_migrated_column = False

    def table(self, _table_name: str) -> Any:
        """Return the configured fake table schema.

        Args:
            _table_name: Table identifier requested by the helper.

        Returns:
            Any: Object exposing the fake schema fields.

        Raises:
            RuntimeError: If schema inspection failure is enabled.
        """
        if self.fail_inspection:
            raise RuntimeError("simulated schema inspection failure")
        return SimpleNamespace(schema=SimpleNamespace(fields=self.fields))

    def sql(self, statement: str) -> None:
        """Record and apply the timestamp ADD COLUMNS statement.

        Args:
            statement: Spark SQL statement issued by the helper.

        Raises:
            RuntimeError: If migration failure is enabled.
        """
        self.statements.append(statement)
        if self.fail_migration:
            raise RuntimeError("simulated migration failure")
        if not self.omit_migrated_column:
            self.fields.append(
                SimpleNamespace(
                    name="processing_timestamp",
                    dataType=_FakeSparkType("timestamp"),
                    nullable=True,
                )
            )


def _field(name: str, type_name: str, nullable: bool = True) -> Any:
    """Create a fake Spark schema field for tests.

    Args:
        name: Schema field name.
        type_name: Spark SQL simple type name.
        nullable: Whether the field accepts NULL values.

    Returns:
        Any: Fake schema field with name, type, and nullability attributes.
    """
    return SimpleNamespace(
        name=name, dataType=_FakeSparkType(type_name), nullable=nullable
    )


class EnsureNullableTimestampColumnTests(unittest.TestCase):
    """Verify additive migration and schema validation behavior."""

    def test_adds_missing_nullable_timestamp_column(self) -> None:
        """Add a missing timestamp field and validate it after migration."""
        spark = _FakeSparkSession()

        ensure_nullable_timestamp_column(
            spark, "`catalog`.`schema`.`table`", "processing_timestamp"
        )

        self.assertEqual(len(spark.statements), 1)
        self.assertIn(
            "ADD COLUMNS (`processing_timestamp` TIMESTAMP)", spark.statements[0]
        )
        self.assertTrue(spark.fields[0].nullable)

    def test_leaves_existing_timestamp_column_unchanged(self) -> None:
        """Avoid DDL when the existing column already has TIMESTAMP type."""
        spark = _FakeSparkSession([_field("processing_timestamp", "timestamp")])

        ensure_nullable_timestamp_column(
            spark, "`catalog`.`schema`.`table`", "processing_timestamp"
        )

        self.assertEqual(spark.statements, [])

    def test_rejects_existing_incompatible_type(self) -> None:
        """Fail before migration when a same-named field has the wrong type."""
        spark = _FakeSparkSession([_field("processing_timestamp", "string")])

        with self.assertRaisesRegex(RuntimeError, "must be TIMESTAMP"):
            ensure_nullable_timestamp_column(
                spark, "`catalog`.`schema`.`table`", "processing_timestamp"
            )

        self.assertEqual(spark.statements, [])

    def test_reports_schema_inspection_failure(self) -> None:
        """Wrap Spark schema inspection errors with the target table context."""
        spark = _FakeSparkSession()
        spark.fail_inspection = True

        with self.assertRaisesRegex(RuntimeError, "Could not inspect schema"):
            ensure_nullable_timestamp_column(
                spark, "`catalog`.`schema`.`table`", "processing_timestamp"
            )

    def test_reports_migration_failure(self) -> None:
        """Wrap Spark DDL errors with the field and table context."""
        spark = _FakeSparkSession()
        spark.fail_migration = True

        with self.assertRaisesRegex(RuntimeError, "Could not add nullable TIMESTAMP"):
            ensure_nullable_timestamp_column(
                spark, "`catalog`.`schema`.`table`", "processing_timestamp"
            )

    def test_rejects_column_missing_after_migration(self) -> None:
        """Fail validation when the post-migration schema lacks the new field."""
        spark = _FakeSparkSession()
        spark.omit_migrated_column = True

        with self.assertRaisesRegex(RuntimeError, "missing timestamp column"):
            ensure_nullable_timestamp_column(
                spark, "`catalog`.`schema`.`table`", "processing_timestamp"
            )


if __name__ == "__main__":
    unittest.main()
