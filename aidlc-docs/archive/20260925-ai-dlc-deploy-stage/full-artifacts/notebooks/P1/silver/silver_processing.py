# Databricks notebook source
# MAGIC %md
# MAGIC # U2 Silver Processing and Quarantine
# MAGIC
# MAGIC Read bronze Delta Change Data Feed changes, maintain the latest valid event per `event_key`, and quarantine malformed records.
# MAGIC The `silver_lookback_days` widget defaults to `0` to resume the checkpoint; a positive value resets the silver checkpoint and replays from the bronze CDF commit timestamp cutoff.
# MAGIC
# MAGIC Outputs: `test_prod.p1_test` and `test_prod.p1_test_kfk_quarantine`.
# MAGIC The silver `attributes` column uses Delta `VARIANT`; runtime must be Databricks Runtime 15.4 LTS or later.

# COMMAND ----------
# Imports

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

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
SILVER_LOOKBACK_WIDGET = "silver_lookback_days"
DEFAULT_LOOKBACK_DAYS = "0"

dbutils.widgets.text(ENVIRONMENT_WIDGET, DEFAULT_ENVIRONMENT)
dbutils.widgets.text(
    SILVER_LOOKBACK_WIDGET, DEFAULT_LOOKBACK_DAYS, "Lookback days"
)
ENVIRONMENT = dbutils.widgets.get(ENVIRONMENT_WIDGET).strip()
if not ENVIRONMENT:
    raise ValueError("Databricks widget 'environment' must not be blank.")
SILVER_LOOKBACK_RAW = dbutils.widgets.get(SILVER_LOOKBACK_WIDGET).strip()

# COMMAND ----------
# Parameters

CONFIG = load_environment_config(ENVIRONMENT, project_root=PROJECT_ROOT)
try:
    SILVER_LOOKBACK_DAYS = int(SILVER_LOOKBACK_RAW)
except ValueError as exc:
    raise ValueError(
        f"Databricks widget '{SILVER_LOOKBACK_WIDGET}' must be a non-negative integer."
    ) from exc
if SILVER_LOOKBACK_DAYS < 0:
    raise ValueError(
        f"Databricks widget '{SILVER_LOOKBACK_WIDGET}' must be a non-negative integer."
    )
TASK_STARTED_AT_UTC = datetime.now(timezone.utc)
SILVER_REPLAY_CUTOFF_UTC = (
    TASK_STARTED_AT_UTC - timedelta(days=SILVER_LOOKBACK_DAYS)
    if SILVER_LOOKBACK_DAYS > 0
    else None
)
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

def _reset_checkpoint(checkpoint_uri: str) -> None:
    """Remove this notebook's existing checkpoint before an explicit replay.

    Args:
        checkpoint_uri: Exact S3 URI owned by the silver streaming query.

    Raises:
        ValueError: If the checkpoint URI does not identify a leaf path.
        RuntimeError: If the checkpoint exists but cannot be removed.
        Exception: If checkpoint storage cannot be listed or accessed.
    """
    parent_uri, separator, checkpoint_name = checkpoint_uri.rstrip("/").rpartition("/")
    if not separator or not parent_uri or not checkpoint_name:
        raise ValueError("Silver checkpoint URI must include a parent and leaf path.")

    dbutils.fs.mkdirs(parent_uri)
    existing_names = {
        entry.name.rstrip("/") for entry in dbutils.fs.ls(parent_uri)
    }
    if checkpoint_name in existing_names:
        if not dbutils.fs.rm(checkpoint_uri, recurse=True):
            raise RuntimeError(
                f"Could not reset silver streaming checkpoint at {checkpoint_uri}."
            )
        print(f"Reset silver streaming checkpoint at {checkpoint_uri}.")
    else:
        print(f"No existing silver streaming checkpoint found at {checkpoint_uri}.")


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


def _process_cdf_batch(
    change_batch: DataFrame, batch_id: int, replay_summary: dict[str, Any]
) -> None:
    """Process one bronze CDF micro-batch and fail it unless both outputs persist.

    Args:
        change_batch: Bronze Change Data Feed records for one stream micro-batch.
        batch_id: Structured Streaming micro-batch identifier, used for run logging.
        replay_summary: Mutable run summary updated with observed CDF commit timestamps.

    Raises:
        ValueError: If the append-only bronze contract produces a non-insert CDF row.
        Exception: If parsing, source access, or either output persistence fails. The
            exception propagates so the stream checkpoint does not advance the batch.
    """
    batch_summary = change_batch.agg(
        F.count(F.lit(1)).alias("record_count"),
        F.min("_commit_timestamp").alias("first_commit_timestamp"),
    ).first()
    if batch_summary["record_count"]:
        replay_summary["source_records_observed"] = True
        observed_timestamp = batch_summary["first_commit_timestamp"]
        current_first = replay_summary["first_observed_source_timestamp"]
        if observed_timestamp is not None and (
            current_first is None or observed_timestamp < current_first
        ):
            replay_summary["first_observed_source_timestamp"] = observed_timestamp

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


def run_silver_processing(
    environment: str, lookback_days: int, replay_cutoff_utc: datetime | None
) -> None:
    """Run the available bronze CDF changes and wait for the daily stream to finish.

    Args:
        environment: Environment name selected by the notebook widget.
        lookback_days: Number of days to replay; zero resumes the existing checkpoint.
        replay_cutoff_utc: UTC cutoff timestamp for a positive lookback, otherwise None.

    Raises:
        RuntimeError: If source CDF or output table prerequisites are missing.
        Exception: If Delta source processing or either output write fails.
    """
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    _ensure_output_tables()
    _require_bronze_cdf()

    if lookback_days > 0:
        _reset_checkpoint(SILVER_CHECKPOINT)

    source_reader = spark.readStream.format("delta").option("readChangeFeed", "true")
    if replay_cutoff_utc is not None:
        source_reader = source_reader.option(
            "startingTimestamp",
            replay_cutoff_utc.isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            ),
        )
    source = source_reader.table(BRONZE_TABLE)
    if replay_cutoff_utc is not None:
        source = source.filter(
            F.col("_commit_timestamp") >= F.lit(replay_cutoff_utc)
        )
    replay_summary: dict[str, Any] = {
        "layer": "silver",
        "lookback_days": lookback_days,
        "requested_cutoff_utc": (
            replay_cutoff_utc.isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            )
            if replay_cutoff_utc is not None
            else None
        ),
        "first_observed_source_timestamp": None,
        "source_records_observed": False,
    }
    query = (
        source.writeStream.foreachBatch(
            lambda batch, batch_id: _process_cdf_batch(
                batch, batch_id, replay_summary
            )
        )
        .option("checkpointLocation", SILVER_CHECKPOINT)
        .trigger(availableNow=True)
        .start()
    )
    query.awaitTermination()
    first_observed_timestamp = replay_summary["first_observed_source_timestamp"]
    replay_summary["observed_window_shortened"] = None
    if replay_cutoff_utc is not None and first_observed_timestamp is not None:
        first_observed_utc = first_observed_timestamp.replace(tzinfo=timezone.utc)
        replay_summary["observed_window_shortened"] = (
            first_observed_utc > replay_cutoff_utc
        )
        replay_summary["first_observed_source_timestamp"] = (
            first_observed_utc.isoformat().replace("+00:00", "Z")
        )
    elif first_observed_timestamp is not None:
        replay_summary["first_observed_source_timestamp"] = (
            first_observed_timestamp.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    replay_summary["environment"] = environment
    replay_summary["source_table"] = BRONZE_TABLE
    print(json.dumps(replay_summary, sort_keys=True))

# COMMAND ----------
# Main Execution

if __name__ == "__main__":
    run_silver_processing(
        ENVIRONMENT,
        SILVER_LOOKBACK_DAYS,
        SILVER_REPLAY_CUTOFF_UTC,
    )
