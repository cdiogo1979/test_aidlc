# Unit Test Execution

Run the complete repository suite with:

```bash
python3 -m unittest discover -s tests
```

The P2 property tests extract the pure topic resolver and JAAS quoting helper from the notebook AST, so Spark/Databricks modules are not required. Hypothesis runs deterministic generated cases with shrinking enabled. The successful run recorded 25 tests, including the P2 properties; see `build-and-test-summary.md` for the Hypothesis version used.
