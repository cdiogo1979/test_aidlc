# Business Overview

## Business Context

The repository contains Databricks workloads that ingest Kafka events, persist raw records in Delta bronze, and transform valid event data into silver current-state tables while retaining invalid records in quarantine.

## P1 Business Transactions

- Daily ingestion and processing: read the configured Kafka topic, persist source records, then process bronze records into silver and quarantine.

## P1 Responsibilities

- Bronze ingestion acquires and preserves Kafka records.
- Silver processing validates JSON, selects the current event per key, and quarantines invalid data.
- The P1 Databricks job runs bronze before silver.
