# U2 Code Generation Clarification Questions

## Question 1 — Encoding extensible JSON attributes

The approved Functional Design stores every non-`event_key` JSON property, including nested values, in an extensible attributes map. Which Delta representation should U2 use?

A) Store `attributes` as a Databricks `VARIANT` object (Recommended for preserving/querying arbitrary JSON types). This requires Databricks Runtime 15.4 LTS or later for Delta table reads/writes with variant support enabled; enabling it upgrades the Delta writer protocol and may affect older external clients. See [Databricks VARIANT table support](https://docs.databricks.com/aws/en/tables/features/variant) and [VARIANT data type](https://docs.databricks.com/aws/en/sql/language-manual/data-types/variant-type).

B) Store `attributes` as a JSON string for broader runtime/client compatibility; consumers parse the string when querying nested values.

X) Other (please describe after `[Answer]:`)

[Answer]:A
