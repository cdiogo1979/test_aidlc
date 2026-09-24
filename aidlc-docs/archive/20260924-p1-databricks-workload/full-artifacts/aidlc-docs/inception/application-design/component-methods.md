# P1 Component Methods

These are high-level interface signatures. Detailed parsing, ordering, merge, checkpoint, and error-handling rules belong in Functional Design.

## Bronze Ingestion Notebook

```python
def load_environment_config(environment: str) -> P1Config:
    """Load the selected environment YAML for this notebook."""

def run_bronze_ingestion(environment: str) -> BronzeWriteSummary:
    """Read new Kafka records and persist the source payload and metadata."""
```

**Inputs**: Environment name; Kafka topic, hosts, and secret reference from `P1Config`.  
**Output**: `BronzeWriteSummary` containing high-level write counts/status, with no secret values.

## Silver Transformation Notebook

```python
def load_environment_config(environment: str) -> P1Config:
    """Load the selected environment YAML for this notebook."""

def run_silver_transformation(environment: str) -> SilverRunSummary:
    """Read bronze records, update silver current state, and quarantine malformed records."""
```

**Inputs**: Environment name; bronze/silver/quarantine table settings from `P1Config`.  
**Output**: `SilverRunSummary` containing high-level merge/quarantine counts and task status.

## P1 Daily Job

The Databricks job is configured declaratively in JSON rather than implemented as a Python method.

- **Input parameter**: `environment: str` passed to both notebook tasks.
- **Task sequence**: Bronze notebook, then Silver notebook on bronze success.
- **Output**: Databricks task/job status and notebook summaries.

## Type Notes

- `P1Config`, `BronzeWriteSummary`, and `SilverRunSummary` are conceptual interface types; their concrete schemas are defined during Units Generation and Functional Design.
- Spark `DataFrame` processing types remain internal to the notebooks at this design level.
