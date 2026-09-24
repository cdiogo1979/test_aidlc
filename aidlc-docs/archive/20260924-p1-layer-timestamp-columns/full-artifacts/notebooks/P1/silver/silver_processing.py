# Databricks notebook source
# MAGIC %md
# MAGIC # U2 Silver Processing and Quarantine
# MAGIC
# MAGIC Read bronze Delta Change Data Feed changes, maintain the latest valid event per `event_key`, and quarantine malformed records.
# MAGIC
# MAGIC Outputs: `test_prod.p1_test` and `test_prod.p1_test_kfk_quarantine`.
# MAGIC The silver `attributes` column uses Delta `VARIANT`; runtime must be Databricks Runtime 15.4 LTS or later.

# COMMAND ----------
# Imports

from __future__ import annotations

import os
import sys
from pathlib import Path

from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql import Window
from pyspark.sql import functions as F


_configured_project_root = os.environ.get("P1_PROJECT_ROOT")
_project_root_candidates = [Path(_configured_project_root)] if _configured_project_root else []
_current_directory = Path.cwd().resolve()
_project_root_candidates.append(_current_directory)
_project_root_candidates.extend(_current_directory.parents)

for _candidate in _project_root_candidates:
    _candidate_root = _candidate.resolve()
    if (_candidate_root / "src" / "common.py").is_file():
        _candidate_root_text = str(_candidate_root)
        if _candidate_root_text not in sys.path:
            sys.path.insert(0, _candidate_root_text)
        PROJECT_ROOT = _candidate_root
        break
else:
    raise FileNotFoundError(
        "Could not locate src/common.py from the notebook working directory. "
        "Set P1_PROJECT_ROOT to the deployed project root if needed."
    )

from src.common import load_environment_config, quote_qualified_identifier, required_text
from src.delta_schema import ensure_nullable_timestamp_column

# COMMAND ----------
# Widgets

ENVIRONMENT_WIDGET = "environment"
DEFAULT_ENVIRONMENT = "prod"

dbutils.widgets.text(ENVIRONMENT_WIDGET, DEFAULT_ENVIRONMENT)
ENVIRONMENT = dbutils.widgets.get(ENVIRONMENT_WIDGET).strip()
if not ENVIRONMENT:
    raise ValueError("Databricks widget 'environment' must not be blank.")

# COMMAND ----------
# Parameters

CONFIG = load_environment_config(ENVIRONMENT, project_root=PROJECT_ROOT)
DATABASE_SQL = quote_qualified_identifier(required_text(CONFIG, "database", "database"))
DATA_PATH = required_text(CONFIG, "data_path", "data_path").rstrip("/")

if not DATA_PATH.startswith("s3://"):
    raise ValueError("Configured data_path must be an S3 URI for this deployment.")

BRONZE_TABLE = f"{DATABASE_SQL}.`p1_test_kfk_brz`"
SILVER_TABLE = f"{DATABASE_SQL}.`p1_test`"
QUARANTINE_TABLE = f"{DATABASE_SQL}.`p1_test_kfk_quarantine`"
SILVER_CHECKPOINT = f"{DATA_PATH}/checkpoints/P1/silver_processing"
VARIANT_RUNTIME_REQUIREMENT = "Databricks Runtime 15.4 LTS or later"

# COMMAND ----------
# Additional Functions

def _ensure_output_tables() -> None:
    """Create the U2 output tables when absent and validate the silver VARIANT column.

    Raises:
        RuntimeError: If the silver table cannot be created with or does not contain
            the required Delta VARIANT attributes column.
    """
    try:
        spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS {SILVER_TABLE} (
                `event_key` STRING,
                `attributes` VARIANT,
                `topic` STRING,
                `partition` INT,
                `offset` BIGINT,
                `source_timestamp` TIMESTAMP,
                `silver_processing_timestamp` TIMESTAMP
            ) USING DELTA
            TBLPROPERTIES ('delta.enableVariant' = 'true')
            """
        )
        spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS {QUARANTINE_TABLE} (
                `raw_payload` BINARY,
                `topic` STRING,
                `partition` INT,
                `offset` BIGINT,
                `source_timestamp` TIMESTAMP,
                `ingestion_timestamp` TIMESTAMP,
                `error` STRING
            ) USING DELTA
            """
        )
        spark.sql(
            f"ALTER TABLE {SILVER_TABLE} "
            "SET TBLPROPERTIES ('delta.enableVariant' = 'true')"
        )
        silver_schema = spark.table(SILVER_TABLE).schema
        attributes_field = next(
            (field for field in silver_schema.fields if field.name == "attributes"),
            None,
        )
        if (
            attributes_field is None
            or attributes_field.dataType.simpleString().lower() != "variant"
        ):
            raise RuntimeError(
                f"Silver table {SILVER_TABLE} must have an `attributes VARIANT` column. "
                f"Use {VARIANT_RUNTIME_REQUIREMENT} and migrate the table schema if needed."
            )
    except Exception as exc:
        if isinstance(exc, RuntimeError) and "attributes VARIANT" in str(exc):
            raise
        raise RuntimeError(
            f"Could not initialize U2 Delta tables with the required VARIANT support. "
            f"Use {VARIANT_RUNTIME_REQUIREMENT} and enable Delta VARIANT table support."
        ) from exc

    ensure_nullable_timestamp_column(
        spark, SILVER_TABLE, "silver_processing_timestamp"
    )


def _require_bronze_cdf() -> None:
    """Confirm Delta Change Data Feed is enabled on the bronze source table.

    Raises:
        RuntimeError: If the bronze table is missing or CDF is not enabled.
    """
    try:
        property_row = spark.sql(
            f"SHOW TBLPROPERTIES {BRONZE_TABLE} ('delta.enableChangeDataFeed')"
        ).first()
    except Exception as exc:
        raise RuntimeError(
            f"Could not inspect CDF settings for {BRONZE_TABLE}. "
            "Run the U1 bronze task after its CDF enablement change."
        ) from exc

    if property_row is None or str(property_row["value"]).lower() != "true":
        raise RuntimeError(
            f"Delta Change Data Feed is not enabled on {BRONZE_TABLE}. "
            "Run the updated U1 bronze task before U2."
        )


def _classify_bronze_records(records: DataFrame) -> DataFrame:
    """Parse JSON payloads and classify records using the approved event-key contract.

    Args:
        records: Bronze CDF insert records with raw payload and Kafka metadata.

    Returns:
        DataFrame: Input rows with parsed payload, event key, and nullable error text.
    """
    parsed = (
        records.withColumn("_payload_json", F.decode(F.col("value"), "UTF-8"))
        .withColumn("_payload_variant", F.try_parse_json(F.col("_payload_json")))
        .withColumn("_root_schema", F.schema_of_variant(F.col("_payload_variant")))
        .withColumn(
            "_event_key_variant",
            F.try_variant_get(F.col("_payload_variant"), "$.event_key", "VARIANT"),
        )
        .withColumn(
            "_event_key_schema", F.schema_of_variant(F.col("_event_key_variant"))
        )
        .withColumn(
            "event_key",
            F.when(
                F.col("_event_key_schema") == F.lit("STRING"),
                F.try_variant_get(
                    F.col("_payload_variant"), "$.event_key", "STRING"
                ),
            ),
        )
    )

    is_object = F.coalesce(F.col("_root_schema").startswith("OBJECT<"), F.lit(False))
    is_string_key = F.coalesce(
        F.col("_event_key_schema") == F.lit("STRING"), F.lit(False)
    )
    has_nonblank_key = F.coalesce(
        F.length(F.trim(F.col("event_key"))) > 0, F.lit(False)
    )

    return parsed.withColumn(
        "_error",
        F.when(F.col("_payload_variant").isNull(), F.lit("Invalid JSON payload."))
        .when(~is_object, F.lit("JSON root must be an object."))
        .when(~is_string_key, F.lit("event_key must be a JSON string."))
        .when(~has_nonblank_key, F.lit("event_key must not be blank.")),
    )


def _silver_rows(valid_records: DataFrame) -> DataFrame:
    """Build silver rows with non-key JSON properties stored as a VARIANT object.

    Args:
        valid_records: Classified records with a valid event key and parsed object.

    Returns:
        DataFrame: Silver rows with `event_key`, `attributes`, and source metadata.
    """
    valid_records.createOrReplaceTempView("_u2_valid_bronze_records")
    attributes = spark.sql(
        """
        SELECT
            source.topic AS topic,
            source.`partition` AS `partition`,
            source.`offset` AS `offset`,
            to_variant_object(
                map_from_entries(
                    collect_list(
                        named_struct('key', exploded.key, 'value', exploded.value)
                    ) FILTER (
                        WHERE exploded.key IS NOT NULL
                          AND exploded.key <> 'event_key'
                    )
                )
            ) AS attributes
        FROM _u2_valid_bronze_records AS source,
             LATERAL variant_explode_outer(source._payload_variant) AS exploded
        GROUP BY source.topic, source.`partition`, source.`offset`
        """
    )

    event_rows = valid_records.select(
        F.col("event_key"),
        F.col("topic"),
        F.col("partition"),
        F.col("offset"),
        F.col("source_timestamp"),
        F.current_timestamp().alias("silver_processing_timestamp"),
    )
    return (
        event_rows.join(attributes, ["topic", "partition", "offset"], "inner")
        .select(
            "event_key",
            "attributes",
            "topic",
            "partition",
            "offset",
            "source_timestamp",
            "silver_processing_timestamp",
        )
    )


def _write_silver(valid_records: DataFrame) -> int:
    """Idempotently merge the latest valid event for each key into silver.

    Args:
        valid_records: Classified bronze records that passed JSON/key validation.

    Returns:
        int: Number of per-key candidate rows submitted to the silver merge.
    """
    candidates = _silver_rows(valid_records)
    latest_per_key = Window.partitionBy("event_key").orderBy(
        F.col("source_timestamp").desc_nulls_last(),
        F.col("partition").desc(),
        F.col("offset").desc(),
    )
    source = (
        candidates.withColumn("_row_number", F.row_number().over(latest_per_key))
        .filter(F.col("_row_number") == 1)
        .drop("_row_number")
    )
    candidate_count = source.count()
    if candidate_count == 0:
        return 0

    later_source_condition = """
        (source.`source_timestamp` IS NOT NULL AND target.`source_timestamp` IS NULL)
        OR source.`source_timestamp` > target.`source_timestamp`
        OR (
            source.`source_timestamp` <=> target.`source_timestamp`
            AND (
                source.`partition` > target.`partition`
                OR (
                    source.`partition` = target.`partition`
                    AND source.`offset` > target.`offset`
                )
            )
        )
    """
    target = DeltaTable.forName(spark, SILVER_TABLE).alias("target")
    source_alias = source.alias("source")
    (
        target.merge(source_alias, "target.`event_key` = source.`event_key`")
        .whenMatchedUpdateAll(condition=later_source_condition)
        .whenNotMatchedInsertAll()
        .execute()
    )
    return candidate_count


def _write_quarantine(invalid_records: DataFrame) -> int:
    """Idempotently write malformed source records and safe diagnostics to quarantine.

    Args:
        invalid_records: Classified records with a non-empty parse/validation error.

    Returns:
        int: Number of distinct invalid source identities submitted to quarantine.
    """
    quarantine_rows = (
        invalid_records.select(
            F.col("value").alias("raw_payload"),
            F.col("topic"),
            F.col("partition"),
            F.col("offset"),
            F.col("source_timestamp"),
            F.current_timestamp().alias("ingestion_timestamp"),
            F.col("_error").alias("error"),
        )
        .dropDuplicates(["topic", "partition", "offset"])
    )
    record_count = quarantine_rows.count()
    if record_count == 0:
        return 0

    target = DeltaTable.forName(spark, QUARANTINE_TABLE).alias("target")
    source = quarantine_rows.alias("source")
    identity_condition = (
        "target.`topic` = source.`topic` "
        "AND target.`partition` = source.`partition` "
        "AND target.`offset` = source.`offset`"
    )
    target.merge(source, identity_condition).whenNotMatchedInsertAll().execute()
    return record_count


def _process_cdf_batch(change_batch: DataFrame, batch_id: int) -> None:
    """Process one bronze CDF micro-batch and fail it unless both outputs persist.

    Args:
        change_batch: Bronze Change Data Feed records for one stream micro-batch.
        batch_id: Structured Streaming micro-batch identifier, used for run logging.

    Raises:
        ValueError: If the append-only bronze contract produces a non-insert CDF row.
        Exception: If parsing, source access, or either output persistence fails. The
            exception propagates so the stream checkpoint does not advance the batch.
    """
    change_types = {
        row["_change_type"]
        for row in change_batch.select("_change_type").distinct().collect()
    }
    unexpected_types = change_types - {"insert"}
    if unexpected_types:
        raise ValueError(
            "U2 expects insert-only bronze CDF records; found unsupported change types: "
            + ", ".join(sorted(str(change_type) for change_type in unexpected_types))
        )

    inserts = (
        change_batch.filter(F.col("_change_type") == F.lit("insert"))
        .drop("_change_type", "_commit_version", "_commit_timestamp")
        .dropDuplicates(["topic", "partition", "offset"])
    )
    if not inserts.take(1):
        return

    classified = _classify_bronze_records(inserts)
    valid_records = classified.filter(F.col("_error").isNull())
    invalid_records = classified.filter(F.col("_error").isNotNull())
    valid_count = valid_records.count()
    invalid_count = invalid_records.count()

    silver_candidates = _write_silver(valid_records) if valid_count else 0
    quarantined = _write_quarantine(invalid_records) if invalid_count else 0
    print(
        f"U2 batch {batch_id} completed: valid records={valid_count}, "
        f"silver candidates={silver_candidates}, quarantine candidates={quarantined}."
    )


def run_silver_processing() -> None:
    """Run the available bronze CDF changes and wait for the daily stream to finish.

    Raises:
        RuntimeError: If source CDF or output table prerequisites are missing.
        Exception: If Delta source processing or either output write fails.
    """
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    _ensure_output_tables()
    _require_bronze_cdf()

    source = (
        spark.readStream.format("delta")
        .option("readChangeFeed", "true")
        .table(BRONZE_TABLE)
    )
    query = (
        source.writeStream.foreachBatch(_process_cdf_batch)
        .option("checkpointLocation", SILVER_CHECKPOINT)
        .trigger(availableNow=True)
        .start()
    )
    query.awaitTermination()
    print(
        f"U2 Silver Processing completed for environment '{ENVIRONMENT}' "
        f"from bronze CDF table {BRONZE_TABLE}."
    )

# COMMAND ----------
# Main Execution

if __name__ == "__main__":
    run_silver_processing()
