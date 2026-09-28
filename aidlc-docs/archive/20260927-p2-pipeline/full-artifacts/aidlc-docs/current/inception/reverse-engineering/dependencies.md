# Dependencies

## Runtime Flow

- P1 job depends on the bronze notebook and then the silver notebook.
- Silver depends on the bronze Delta table and its CDF history.
- Both notebooks depend on environment configuration, shared project utilities, and Databricks runtime services.
- Bronze depends on Kafka connectivity and secret-backed credentials.
- Both layers depend on their own Delta checkpoint locations.

## External Services

- Databricks compute, Jobs, workspace file synchronization, and Secrets.
- Kafka cluster configured per environment.
- Storage backing Delta tables and checkpoints.
