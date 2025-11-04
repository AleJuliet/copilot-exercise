# Test Documentation

This directory contains comprehensive tests for the Mergington High School Activities API.

## Test Structure

### `test_api.py`
Main API endpoint tests covering:
- **Root Endpoint**: Redirect behavior
- **Activities Endpoint**: Data retrieval and structure validation
- **Signup Endpoint**: Student registration functionality
- **Unregister Endpoint**: Student unregistration functionality
- **Integration Tests**: Complete signup/unregister workflows
- **Email Validation**: Special character handling
- **Data Persistence**: State management across requests

### `test_static.py`
Static file serving tests covering:
- HTML file accessibility and content validation
- CSS file serving and content checks
- JavaScript file serving and function presence
- 404 handling for non-existent files
- Root redirect functionality

### `test_edge_cases.py`
Edge cases and robustness tests covering:
- **Edge Cases**: Special characters, unicode, long emails, case sensitivity
- **Concurrency**: Rapid operations and state consistency
- **Data Integrity**: Participant counts, duplicates, cross-activity independence

## Running Tests

### Quick Start
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_api.py -v

# Run specific test
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v
```

### Using the Test Runner
```bash
./run_tests.sh
```

## Test Coverage

The test suite achieves **100% code coverage** on the backend application, ensuring all code paths are tested.

## Test Environment

Tests use FastAPI's `TestClient` which:
- Provides isolated test environment
- Resets data state between tests
- Simulates real HTTP requests without network overhead
- Maintains session consistency

## Fixtures

- `client`: FastAPI test client instance
- `reset_activities`: Resets activity data to initial state before each test

## Test Categories

1. **Happy Path Tests**: Normal usage scenarios
2. **Error Handling Tests**: Invalid inputs and edge cases
3. **Integration Tests**: Multi-step workflows
4. **Data Integrity Tests**: State consistency and validation
5. **Static File Tests**: Frontend resource serving

## Dependencies

- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for FastAPI TestClient