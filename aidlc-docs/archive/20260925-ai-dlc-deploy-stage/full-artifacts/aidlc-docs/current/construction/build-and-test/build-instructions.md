# Build Instructions: P1 Streaming Lookback

## Build Status

The change consists of Databricks notebook source and a Databricks Declarative Automation Bundle. There is no local compile/package build target for these artifacts. The Databricks CLI is not installed in the current environment, so Bundle validation could not be performed here.

## Prerequisites for Bundle Validation

- Install a Databricks CLI version compatible with Declarative Automation Bundles.
- Configure access to the intended workspace and the `prod` target's required variables.
- Use the repository's established deployment identity and approved configuration; do not place secrets in notebook or job files.

## Build/Validation Steps

From `jobs/P1/`, validate the Bundle before deployment:

```bash
databricks bundle validate -t prod
```

Expected result: the CLI reports a valid Bundle and resolves the job resource, notebook paths, target variables, and the `environment`, `bronze_lookback_days`, and `silver_lookback_days` parameters. This validation does not execute notebooks or prove Kafka, Delta CDF, or checkpoint behavior.

Bundle deployment is outside this Build and Test stage; deployment instructions belong to the Deploy handoff and require separate approval.
