---
name: run-tests
description: Use to run PMHelper's test suite, interpret failures, and write a new test. Reach for this after changing code, before committing, or when you want to verify something works.
---

# Run & write tests (PMHelper)

## Where tests live
- `tests/` — the **automated** suite (~1288 tests). This is what `pytest` runs.
  Config is in `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths=["tests"]`,
  coverage on `src/pmhelper`).
- `tests/server/` — API/database/integration tests (has its own `conftest.py`).
- `manual_tests/` — interactive GUI tests and legacy scripts. **Excluded** from the
  automated run on purpose (they open windows or reference removed modules). Run
  these by hand only.

## Run them
```bash
pytest                        # whole automated suite, with coverage
pytest tests/test_evm_calculations_edu.py        # one file
pytest tests/test_evm_calculations_edu.py::test_cpi  # one test
pytest -k "evm and not io"    # by keyword
pytest --no-cov -q            # faster, no coverage
```

Known pre-existing failures: `tests/test_api.py` and `tests/test_selection_unit.py`
error on collection because they import the long-removed `pmhelper.core.models`.
These are not your fault if you didn't touch them — but they're good first fixes.

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
