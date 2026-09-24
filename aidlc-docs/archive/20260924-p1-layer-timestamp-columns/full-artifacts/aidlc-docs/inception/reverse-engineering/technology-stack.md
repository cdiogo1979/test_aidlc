# Technology Stack

## Programming Languages

- **Python** — notebooks, shared configuration helper, and lifecycle tooling.
- **YAML** — environment and Databricks Bundle configuration.

## Frameworks and Libraries

- **Apache Spark / PySpark** — notebook data processing and Structured Streaming.
- **Delta Lake** — bronze, silver, and quarantine tables; CDF and merge operations.
- **Databricks Declarative Automation Bundles** — job deployment configuration.
- **PyYAML** — environment configuration parsing.
- **Python `unittest`** — lifecycle utility tests only.

## Infrastructure

- **Databricks workspace and job compute** — deployment target; not authenticated or available here.
- **Apache Kafka** — configured event source.
- **Amazon S3** — configured data/checkpoint location.
- **Databricks Secrets** — Kafka password storage.

## Build and Runtime Notes

- No lockfile or dependency manifest was found in the project root.
- P1 silver requires a Databricks Runtime that supports Delta `VARIANT`; project documentation specifies 15.4 LTS or later.
- Bundle CLI schema/authentication validation and notebook execution have not been performed.
