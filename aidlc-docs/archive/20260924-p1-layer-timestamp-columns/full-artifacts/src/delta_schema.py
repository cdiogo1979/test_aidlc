"""Schema helpers for the P1 Databricks workload."""

from __future__ import annotations

from typing import Any


def ensure_nullable_timestamp_column(
    spark: Any, table_name: str, column_name: str
) -> None:
    """Add and validate a nullable TIMESTAMP column before table writes.

    The table must already exist. Existing rows are not updated; Delta's additive
    column migration leaves their values NULL.

    Args:
        spark: SparkSession-like object with ``table`` and ``sql`` methods.
        table_name: Fully qualified table identifier, quoted for Spark SQL.
        column_name: Unquoted SQL identifier for the timestamp column.

    Raises:
        ValueError: If ``column_name`` is not a simple SQL identifier.
        RuntimeError: If schema inspection, migration, or type validation fails.
    """
    if not column_name.isidentifier():
        raise ValueError(
            f"Timestamp column name must be a simple SQL identifier: {column_name!r}."
        )

    try:
        schema = spark.table(table_name).schema
    except Exception as exc:
        raise RuntimeError(
            f"Could not inspect schema for Delta table {table_name}."
        ) from exc

    existing_field = next(
        (field for field in schema.fields if field.name == column_name), None
    )
    if existing_field is not None:
        _validate_timestamp_type(existing_field, table_name, column_name)
        return

    try:
        spark.sql(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMNS (`{column_name}` TIMESTAMP)"
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not add nullable TIMESTAMP column `{column_name}` "
            f"to Delta table {table_name}."
        ) from exc

    try:
        migrated_schema = spark.table(table_name).schema
    except Exception as exc:
        raise RuntimeError(
            f"Could not validate schema for Delta table {table_name} "
            "after timestamp-column migration."
        ) from exc

    migrated_field = next(
        (field for field in migrated_schema.fields if field.name == column_name), None
    )
    if migrated_field is None:
        raise RuntimeError(
            f"Delta table {table_name} is missing timestamp column `{column_name}` "
            "after migration."
        )
    _validate_timestamp_type(migrated_field, table_name, column_name)


def _validate_timestamp_type(field: Any, table_name: str, column_name: str) -> None:
    """Raise when an existing schema field is not a Spark TIMESTAMP.

    Args:
        field: Spark schema field to inspect.
        table_name: Fully qualified table identifier for the error message.
        column_name: Expected timestamp column name.

    Raises:
        RuntimeError: If the field's Spark SQL type is not ``TIMESTAMP``.
    """
    actual_type = field.dataType.simpleString().lower()
    if actual_type != "timestamp":
        raise RuntimeError(
            f"Delta table {table_name} column `{column_name}` must be TIMESTAMP; "
            f"found {actual_type.upper()}."
        )
