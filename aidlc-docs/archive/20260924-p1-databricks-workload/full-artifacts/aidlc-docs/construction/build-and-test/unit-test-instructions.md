# Unit Test Instructions

## Existing automated suite

Run the repository's existing standard-library test suite from the repository root:

```bash
python3 -B -m unittest discover -s tests -v
```

The suite covers the AI-DLC artifact-compaction utility in `scripts/aidlc_intent.py`; it does not exercise the P1 Databricks notebooks. The suite was run during this stage: **13 passed, 0 failed**.

## P1 source checks

Check syntax for the shared library and both Databricks notebook source files:

```bash
python3 -B -c 'from pathlib import Path; files = [Path("src/common.py"), *Path("notebooks/P1").rglob("*.py")]; [compile(p.read_text(encoding="utf-8"), str(p), "exec") for p in files]; print(f"Syntax OK for {len(files)} Python files")'
```

This check passed for three files. It compiles source without executing notebook code or requiring Spark, `dbutils`, Kafka, or Delta.

No P1 Spark-specific unit test suite or local Spark dependency setup exists. Do not treat the compaction tests or Python syntax check as verification of Kafka ingestion, Delta operations, CDF handling, VARIANT parsing, quarantine behavior, or checkpoint recovery. Those behaviors require the isolated Databricks integration environment described in `integration-test-instructions.md`.
