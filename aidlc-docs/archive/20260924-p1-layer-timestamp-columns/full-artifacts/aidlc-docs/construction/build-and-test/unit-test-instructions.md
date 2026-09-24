# Unit Test Execution — U4 P1 Layer Timestamp Metadata

## Run All Local Unit Tests

From the project root:

```bash
python3 -m unittest discover -s tests -v
```

The suite uses Python's standard library `unittest`; no additional package installation is required for the local test files.

## Expected Coverage

- `tests/test_delta_schema.py`: missing nullable timestamp migration, already-present TIMESTAMP no-op, incompatible type, inspection failure, DDL failure, and missing post-migration field.
- Existing `tests/test_aidlc_intent.py`: regression coverage for unrelated AI-DLC lifecycle utilities.

Spark/Delta integration behavior is not exercised by the fake-Spark tests. No coverage percentage is configured for this repository.

## Results Recorded for This Run

- Python: 3.9.6
- Test command: `python3 -m unittest discover -s tests -v`
- Result: 22 tests passed, 0 failed.
- Syntax check: four changed Python files parsed successfully.

If a test fails, use the failing test name and traceback to identify the helper behavior that diverged, correct the implementation, and rerun the suite before accepting the change.
