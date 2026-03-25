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

The server tests require optional dependencies. Install them with:

```bash
pip install -e .[server,test]
```

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

Tests are marked with the following categories:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.database`: Database-related tests
- `@pytest.mark.slow`: Long-running tests

### Running by Markers

```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v
```

## Graceful Degradation

Tests automatically detect if server components are available:

- If FastAPI dependencies are missing, server tests are skipped
- If SQLAlchemy components are missing, database tests are skipped
- Individual test files handle import errors gracefully

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

Target test coverage areas:

- ✅ **Configuration**: Environment variables, defaults, validation
- ✅ **Database Models**: CRUD operations, relationships, constraints
- ✅ **Analysis Service**: Job processing, error handling, concurrency
- ✅ **API Endpoints**: Request/response handling, validation, error cases
- ✅ **Integration**: End-to-end workflows, performance, edge cases

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
