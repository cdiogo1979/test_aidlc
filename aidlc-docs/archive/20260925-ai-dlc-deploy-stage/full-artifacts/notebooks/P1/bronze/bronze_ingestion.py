# Databricks notebook source
# MAGIC %md
# MAGIC # U1 Bronze Ingestion
# MAGIC
# MAGIC Incrementally ingest Kafka source records into the P1 bronze Delta table.
# MAGIC Preserve Kafka payload and metadata unchanged; enable Delta Change Data Feed for U2.
# MAGIC The `bronze_lookback_days` widget defaults to `0` to resume the checkpoint; a positive value resets the bronze checkpoint and replays from the Kafka record timestamp cutoff.

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
from pyspark.sql import functions as F


_configured_root = os.environ.get("P1_PROJECT_ROOT")
_root_candidates = [Path(_configured_root)] if _configured_root else []
_current_directory = Path.cwd().resolve()
_root_candidates.append(_current_directory)
_root_candidates.extend(_current_directory.parents)

for _candidate in _root_candidates:
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
BRONZE_LOOKBACK_WIDGET = "bronze_lookback_days"
DEFAULT_LOOKBACK_DAYS = "0"

dbutils.widgets.text(ENVIRONMENT_WIDGET, DEFAULT_ENVIRONMENT)
dbutils.widgets.text(
    BRONZE_LOOKBACK_WIDGET, DEFAULT_LOOKBACK_DAYS, "Lookback days"
)
ENVIRONMENT = dbutils.widgets.get(ENVIRONMENT_WIDGET).strip()
if not ENVIRONMENT:
    raise ValueError("Databricks widget 'environment' must not be blank.")
BRONZE_LOOKBACK_RAW = dbutils.widgets.get(BRONZE_LOOKBACK_WIDGET).strip()

# COMMAND ----------
# Parameters

CONFIG = load_environment_config(ENVIRONMENT, project_root=PROJECT_ROOT)
try:
    BRONZE_LOOKBACK_DAYS = int(BRONZE_LOOKBACK_RAW)
except ValueError as exc:
    raise ValueError(
        f"Databricks widget '{BRONZE_LOOKBACK_WIDGET}' must be a non-negative integer."
    ) from exc
if BRONZE_LOOKBACK_DAYS < 0:
    raise ValueError(
        f"Databricks widget '{BRONZE_LOOKBACK_WIDGET}' must be a non-negative integer."
    )
TASK_STARTED_AT_UTC = datetime.now(timezone.utc)
BRONZE_REPLAY_CUTOFF_UTC = (
    TASK_STARTED_AT_UTC - timedelta(days=BRONZE_LOOKBACK_DAYS)
    if BRONZE_LOOKBACK_DAYS > 0
    else None
)
DATABASE_SQL = quote_qualified_identifier(required_text(CONFIG, "database", "database"))
DATA_PATH = required_text(CONFIG, "data_path", "data_path").rstrip("/")
if not DATA_PATH.startswith("s3://"):
    raise ValueError("Configured data_path must be an S3 URI for this deployment.")

BRONZE_TABLE_NAME = "p1_test_kfk_brz"
BRONZE_TABLE = f"{DATABASE_SQL}.`{BRONZE_TABLE_NAME}`"
BRONZE_CHECKPOINT = f"{DATA_PATH}/checkpoints/P1/bronze_ingestion"
BRONZE_COLUMNS_SQL = """
    `value` BINARY,
    `key` BINARY,
    `headers` ARRAY<STRUCT<`key`: STRING, `value`: BINARY>>,
    `topic` STRING,
    `partition` INT,
    `offset` BIGINT,
    `source_timestamp` TIMESTAMP,
    `bronze_ingestion_timestamp` TIMESTAMP
"""

# COMMAND ----------
# Additional Functions

def _jaas_quote(value: str) -> str:
    """Escape a value for use in a quoted Kafka JAAS option.

    Args:
        value: Username or password to escape.

    Returns:
        str: JAAS-escaped value.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _kafka_connection_options(
    kafka_config: dict[str, Any], starting_timestamp_ms: int | None
) -> dict[str, str]:
    """Build Kafka source options from environment settings and Databricks Secrets.

    Args:
        kafka_config: Kafka-specific settings from the environment configuration.
        starting_timestamp_ms: Optional Kafka record timestamp in epoch milliseconds.

    Returns:
        dict[str, str]: Kafka source options for SASL_SSL/PLAIN authentication.

    Raises:
        ValueError: If a required setting is missing or authentication settings differ
            from the approved SASL_SSL/PLAIN contract.
    """
    hosts = required_text(kafka_config, "hosts", "kafka.hosts")
    topic = required_text(kafka_config, "topic", "kafka.topic")
    protocol = required_text(
        kafka_config, "security_protocol", "kafka.security_protocol"
    )
    mechanism = required_text(kafka_config, "sasl_mechanism", "kafka.sasl_mechanism")
    username = required_text(kafka_config, "username", "kafka.username")
    secret_scope = required_text(kafka_config, "secret_scope", "kafka.secret_scope")
    secret_key = required_text(kafka_config, "secret_key", "kafka.secret_key")

    if protocol != "SASL_SSL" or mechanism != "PLAIN":
        raise ValueError("This notebook implements only the approved SASL_SSL/PLAIN contract.")

    password = dbutils.secrets.get(scope=secret_scope, key=secret_key)
    jaas_config = (
        "kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required "
        f'username="{_jaas_quote(username)}" password="{_jaas_quote(password)}";'
    )

    options = {
        "kafka.bootstrap.servers": hosts,
        "subscribe": topic,
        "startingOffsets": "earliest",
        "includeHeaders": "true",
        "kafka.security.protocol": protocol,
        "kafka.sasl.mechanism": mechanism,
        "kafka.sasl.jaas.config": jaas_config,
    }
    if starting_timestamp_ms is not None:
        options["startingTimestamp"] = str(starting_timestamp_ms)
    return options


def _reset_checkpoint(checkpoint_uri: str) -> None:
    """Remove this notebook's existing checkpoint before an explicit replay.

    Args:
        checkpoint_uri: Exact S3 URI owned by the bronze streaming query.

    Raises:
        ValueError: If the checkpoint URI does not identify a leaf path.
        RuntimeError: If the checkpoint exists but cannot be removed.
        Exception: If checkpoint storage cannot be listed or accessed.
    """
    parent_uri, separator, checkpoint_name = checkpoint_uri.rstrip("/").rpartition("/")
    if not separator or not parent_uri or not checkpoint_name:
        raise ValueError("Bronze checkpoint URI must include a parent and leaf path.")

    dbutils.fs.mkdirs(parent_uri)
    existing_names = {
        entry.name.rstrip("/") for entry in dbutils.fs.ls(parent_uri)
    }
    if checkpoint_name in existing_names:
        if not dbutils.fs.rm(checkpoint_uri, recurse=True):
            raise RuntimeError(
                f"Could not reset bronze streaming checkpoint at {checkpoint_uri}."
            )
        print(f"Reset bronze streaming checkpoint at {checkpoint_uri}.")
    else:
        print(f"No existing bronze streaming checkpoint found at {checkpoint_uri}.")


def _ensure_bronze_table(table_name: str) -> None:
    """Create or migrate the bronze table and enable CDF for downstream U2 processing.

    Args:
        table_name: Fully qualified and quoted Delta table identifier.

    Raises:
        Exception: If table creation, CDF inspection, or CDF enablement fails.
    """
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({BRONZE_COLUMNS_SQL})
        USING DELTA
        TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
        """
    )
    ensure_nullable_timestamp_column(
        spark, table_name, "bronze_ingestion_timestamp"
    )
    cdf_property = spark.sql(
        f"SHOW TBLPROPERTIES {table_name} ('delta.enableChangeDataFeed')"
    ).first()
    if cdf_property is None or str(cdf_property["value"]).lower() != "true":
        spark.sql(
            f"""ALTER TABLE {table_name}
                SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')"""
        )


def _write_batch(
    batch_df: DataFrame,
    _batch_id: int,
    table_name: str,
    replay_summary: dict[str, Any],
) -> None:
    """Insert unseen Kafka source identities from one streaming micro-batch.

    Args:
        batch_df: Micro-batch containing Kafka values and source metadata.
        _batch_id: Structured Streaming batch identifier, unused because the merge is
            idempotent by Kafka source identity.
        table_name: Fully qualified and quoted bronze Delta table identifier.
        replay_summary: Mutable run summary updated with observed Kafka timestamps.
    """
    batch_summary = batch_df.agg(
        F.count(F.lit(1)).alias("record_count"),
        F.min("timestamp").alias("first_source_timestamp"),
    ).first()
    if batch_summary["record_count"]:
        replay_summary["source_records_observed"] = True
        observed_timestamp = batch_summary["first_source_timestamp"]
        current_first = replay_summary["first_observed_source_timestamp"]
        if observed_timestamp is not None and (
            current_first is None or observed_timestamp < current_first
        ):
            replay_summary["first_observed_source_timestamp"] = observed_timestamp

    records = batch_df.select(
        F.col("value"),
        F.col("key"),
        F.col("headers"),
        F.col("topic"),
        F.col("partition"),
        F.col("offset"),
        F.col("timestamp").alias("source_timestamp"),
        F.current_timestamp().alias("bronze_ingestion_timestamp"),
    ).dropDuplicates(["topic", "partition", "offset"])

    if not records.take(1):
        return

    target = DeltaTable.forName(spark, table_name).alias("target")
    source = records.alias("source")
    identity_match = (
        "target.`topic` = source.`topic` "
        "AND target.`partition` = source.`partition` "
        "AND target.`offset` = source.`offset`"
    )
    target.merge(source, identity_match).whenNotMatchedInsertAll().execute()


def run_bronze_ingestion(
    environment: str,
    config: dict[str, Any],
    lookback_days: int,
    replay_cutoff_utc: datetime | None,
) -> None:
    """Read available Kafka records and persist them in the bronze Delta table.

    Args:
        environment: Environment name used to load the P1 configuration.
        config: Parsed environment configuration selected by the notebook widget.
        lookback_days: Number of days to replay; zero resumes the existing checkpoint.
        replay_cutoff_utc: UTC cutoff timestamp for a positive lookback, otherwise None.

    Raises:
        ValueError: If required configuration is absent or invalid.
        Exception: If Kafka access, checkpointing, or Delta persistence fails. The
            exception propagates so the Databricks task is marked as failed.
    """
    kafka_config = config.get("kafka")
    if not isinstance(kafka_config, dict):
        raise ValueError("Configuration section 'kafka' must be a YAML mapping.")

    spark.conf.set("spark.sql.session.timeZone", "UTC")
    cutoff_ms = (
        int(replay_cutoff_utc.timestamp() * 1000)
        if replay_cutoff_utc is not None
        else None
    )
    kafka_options = _kafka_connection_options(kafka_config, cutoff_ms)
    _ensure_bronze_table(BRONZE_TABLE)

    if lookback_days > 0:
        _reset_checkpoint(BRONZE_CHECKPOINT)

    source = spark.readStream.format("kafka").options(**kafka_options).load()
    if replay_cutoff_utc is not None:
        source = source.filter(F.col("timestamp") >= F.lit(replay_cutoff_utc))
    replay_summary: dict[str, Any] = {
        "layer": "bronze",
        "lookback_days": lookback_days,
        "requested_cutoff_utc": (
            replay_cutoff_utc.isoformat().replace("+00:00", "Z")
            if replay_cutoff_utc is not None
            else None
        ),
        "first_observed_source_timestamp": None,
        "source_records_observed": False,
    }
    query = (
        source.writeStream.outputMode("append")
        .foreachBatch(
            lambda batch, batch_id: _write_batch(
                batch, batch_id, BRONZE_TABLE, replay_summary
            )
        )
        .option("checkpointLocation", BRONZE_CHECKPOINT)
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
    replay_summary["destination"] = BRONZE_TABLE
    print(json.dumps(replay_summary, sort_keys=True))

# COMMAND ----------
# Main Execution

if __name__ == "__main__":
    run_bronze_ingestion(
        ENVIRONMENT,
        CONFIG,
        BRONZE_LOOKBACK_DAYS,
        BRONZE_REPLAY_CUTOFF_UTC,
    )
