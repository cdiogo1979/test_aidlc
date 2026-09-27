# API and Data Interfaces

## External Interfaces

- Kafka consumer reads the topic configured by the selected environment.
- Databricks Secrets resolve Kafka credentials; secret values are not stored in source.

## Internal Interfaces

- Bronze and silver notebooks receive environment and lookback parameters from the job.
- Bronze Delta is the durable handoff from ingestion to silver CDF processing.
- Bronze output: `<database>.p1_test_kfk_brz`.
- Silver output: `<database>.p1_test`.
- Quarantine output: `<database>.p1_test_kfk_quarantine`.
- The P1 job runs `bronze_ingestion` before dependent `silver_processing`.

No REST or public service API is defined for this workload.
