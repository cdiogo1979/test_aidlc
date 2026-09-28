# P2 Pipeline — Tech Stack Decisions

## Property-Based Testing

- **Framework**: Hypothesis 6.168.1, pinned in `requirements-dev.txt`.
- **Runner**: Python `unittest`, matching the existing repository tests. Hypothesis documents integration with both pytest and unittest ([Hypothesis Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html)).
- **Generation and reproducibility**: Use `@given` with a generated text strategy that exercises quotes and backslashes. Use `@settings(derandomize=True)` and retain default shrinking. Hypothesis documents deterministic generation and failure reproduction in its [settings reference](https://hypothesis.readthedocs.io/en/latest/settings.html).
- **CI**: Add `python -m unittest discover -s tests` to the existing Jenkins pipeline after installing `requirements-dev.txt`, so the property test executes in CI.
- **Rationale**: Python is the workload's language; Hypothesis supplies generated strategies and shrinking and fits the existing unittest-based test suite. The selected version is documented by the official Hypothesis docs as 6.168.1.
