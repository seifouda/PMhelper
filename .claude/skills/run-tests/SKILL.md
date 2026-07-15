---
name: run-tests
description: Use to run PMHelper's test suite, interpret failures, and write a new test. Reach for this after changing code, before committing, or when you want to verify something works.
---

# Run & write tests (PMHelper)

## Where tests live
- `tests/` — the **automated** suite (~1,350 tests and growing). This is what
  `pytest` runs. Config is in `pyproject.toml` (`[tool.pytest.ini_options]`,
  `testpaths=["tests"]`, coverage on `src/pmhelper`).
  Don't trust that number — count it: `pytest --collect-only -q --no-cov | tail -1`.
- `tests/server/` — API/database/integration tests (has its own `conftest.py`).
- `manual_tests/` — interactive GUI tests and demo scripts. **Excluded** from the
  automated run on purpose (`testpaths=["tests"]`) because they open windows or
  print reports rather than assert. Run these by hand only, from the repo root:
  `python manual_tests/test_examples.py`.

## Run them
```bash
pytest                        # whole automated suite, with coverage
pytest tests/test_evm_calculations_edu.py        # one file
pytest tests/test_evm_calculations_edu.py::test_cpi  # one test
pytest -k "evm and not io"    # by keyword
pytest --no-cov -q            # faster, no coverage
```

Some failures in `tests/` are pre-existing and not your fault. Before assuming you
broke something, check whether the same test fails on a clean checkout.

`tests/server/` is the known-bad area: it was written against an older server API
and much of it doesn't run. Don't take its failures as a signal about your change,
and don't "fix" a passing module to match it.

> **`pytest --tb=long` crashes the run** with `INTERNALERROR: MemoryError` inside
> pytest's own traceback formatter. Use `--tb=short` (the configured default) or
> `--tb=no`. If the suite looks like it hangs and dies, this is why.

## Read a failure
`FAILED tests/test_x.py::test_y - AssertionError: assert 5 == 6` → the test expected
`6`, got `5`. Open the test to see what it asserts, then decide whether the **code**
or the **test's expectation** is wrong.

## Write a new test
Mirror an existing `*_edu.py` test. Pattern:
```python
from pmhelper.core.evm_calculations_edu import compute_cpi

def test_cpi_basic():
    assert compute_cpi(ev=100, ac=80) == 1.25
```
Test names start with `test_`; put them in `tests/test_<module>_edu.py`. Prefer
testing the **pure `core/` functions** — they're deterministic and need no GUI.

## Golden rule
Run `pytest` before every commit. If you added a feature, you added tests
([[add-a-feature]]). Report honestly if something fails — don't hide it.
