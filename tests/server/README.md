# PMHelper Server Tests

This directory contains comprehensive unit and integration tests for the PMHelper Desktop Server Mode functionality.

## Test Structure

```
tests/server/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_config.py             # Configuration and settings tests
├── test_database.py           # Database models and operations tests
├── test_analysis_service.py   # Analysis service wrapper tests
├── test_api_endpoints.py      # REST API endpoint tests
└── test_integration.py        # End-to-end integration tests
```

## Test Categories

### Unit Tests

- **Configuration Tests** (`test_config.py`): Server configuration, environment variables, settings validation
- **Database Tests** (`test_database.py`): SQLAlchemy models, CRUD operations, constraints, relationships
- **Service Tests** (`test_analysis_service.py`): Analysis job processing, background tasks, error handling

### Integration Tests

- **API Tests** (`test_api_endpoints.py`): REST endpoint functionality, request/response validation, error handling
- **Integration Tests** (`test_integration.py`): End-to-end workflows, performance testing, concurrent operations

## Running Tests

### Prerequisites

FastAPI, SQLAlchemy and friends are **core** dependencies now, so a plain install
already covers the server itself. You only need the test extra:

```bash
pip install -e ".[test]"
```

There is no `server` extra — the available extras are `postgres`, `dev`, `test`,
and `full`. `.[test]` brings in `pytest-asyncio`, which these tests require: the
fixtures here are async, and without it every test errors with
`AttributeError: 'async_generator' object has no attribute 'get'`.

### Run All Server Tests

```bash
pytest tests/server/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/server/test_config.py tests/server/test_database.py tests/server/test_analysis_service.py -v

# API tests only
pytest tests/server/test_api_endpoints.py -v

# Integration tests only
pytest tests/server/test_integration.py -v
```

### Run with Coverage

```bash
pytest tests/server/ --cov=pmhelper.server --cov-report=html -v
```

## Test Fixtures

### Database Fixtures

- `temp_database`: Temporary SQLite database for isolated testing
- `initialized_database`: Pre-initialized database with schema
- `db_session`: Database session for transactional testing

### Data Fixtures

- `sample_activities_cpm`: Sample CPM project activities
- `sample_activities_pert`: Sample PERT project activities
- `sample_activities_rcps`: Sample RCPS project activities
- `sample_project_minimal`: Minimal project data
- `sample_project_complex`: Complex project with multiple activities

### Application Fixtures

- `test_app`: FastAPI test client with temporary database
- `analysis_service`: Analysis service instance for testing

## Test Markers

Five markers are registered in `conftest.py` (`unit`, `integration`, `api`,
`database`, `slow`), but only two are ever **applied** — `pytest_collection_modifyitems`
adds them by file path:

| Marker | Applied to | Selects anything today? |
|---|---|---|
| `integration` | files with `integration` in the path | ✅ yes |
| `api` | files with `test_api` in the path | ✅ yes |
| `database` | files with `test_database` in the path | ❌ no — that module currently skips at import |
| `unit` | *nothing* — no test declares it | ❌ no |
| `slow` | *nothing* — no test declares it | ❌ no |

### Running by Markers

```bash
# Integration tests
pytest tests/server/ -m integration -v

# API endpoint tests
pytest tests/server/ -m api -v
```

`pytest -m unit` and `pytest -m "not slow"` are **not useful here**: nothing carries
those markers, so the first selects zero tests and the second is a no-op. Don't
read a green `-m unit` run as "the unit tests passed".

## Skips are not "graceful degradation"

This suite used to advertise that it degrades gracefully when FastAPI or SQLAlchemy
are missing. Treat any skip with suspicion instead: **FastAPI and SQLAlchemy are
installed**, so a module-level skip here almost always means the test file imports a
symbol the server no longer exports — real drift, hidden behind a skip that looks
routine. If a module skips, read the ImportError before believing it's optional.

## Test Data

Test data is designed to cover various scenarios:

- **Simple Projects**: Single activity, no dependencies
- **Complex Projects**: Multiple activities with complex dependency chains
- **Edge Cases**: Empty data, invalid inputs, constraint violations
- **Performance Cases**: Concurrent operations, bulk operations

## Continuous Integration

Tests are designed to run in CI environments:

- No external dependencies required
- Temporary files cleaned up automatically
- Environment variables properly isolated
- Deterministic test execution

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure server dependencies are installed:

   ```bash
   pip install fastapi sqlalchemy aiosqlite uvicorn
   ```

2. **Database Errors**: Tests use temporary databases that are cleaned up automatically. If you see persistent database errors, restart your test session.

3. **Timeout Errors**: Integration tests may timeout on slow systems. Increase timeout values in test configuration if needed.

4. **Port Conflicts**: API tests use test clients that don't bind to real ports, so port conflicts shouldn't occur.

### Debug Mode

Run tests with verbose output and no capture to debug issues:

```bash
pytest tests/server/ -v -s --tb=long
```

## Test Coverage

These were the *intended* coverage areas. Three of the five do not currently run —
they skip at import because they reference symbols the server no longer exports.
The ticks below are aspiration, not evidence:

| Area | File | State |
|---|---|---|
| **API Endpoints** — request/response, validation, errors | `test_api_endpoints.py` | ✅ running |
| **Integration** — end-to-end workflows, performance, edge cases | `test_integration.py` | ✅ running |
| **Configuration** — env vars, defaults, validation | `test_config.py` | ⚠️ skips — imports `ServerConfig`; the class is `Config` |
| **Database Models** — CRUD, relationships, constraints | `test_database.py` | ⚠️ skips — imports `AnalysisJobModel`; the model is `AnalysisJob` |
| **Analysis Service** — job processing, errors, concurrency | `test_analysis_service.py` | ⚠️ skips — imports `AnalysisJob` from the service module, which only exports `AnalysisService` |

Re-measure rather than trusting this table — it is a snapshot:

```bash
pytest tests/server/ -q --no-cov --tb=no
```

## Contributing

When adding new server functionality:

1. Add corresponding unit tests for new modules
2. Add integration tests for new API endpoints
3. Update fixtures if new test data patterns are needed
4. Ensure tests handle import errors gracefully
5. Update this README if new test categories are added

## Performance Benchmarks

Integration tests include basic performance validation:

- Concurrent project creation
- Concurrent analysis submission
- Response time validation
- Resource cleanup verification

For detailed performance testing, use dedicated benchmarking tools.
