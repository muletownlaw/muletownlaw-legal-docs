# Test Suite for Document Assembly App

This directory contains automated tests for the legal document generators.

## Setup

Install testing dependencies:

```bash
pip install pytest pytest-cov python-docx
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest tests/test_regression.py
pytest tests/test_poa_generator.py
```

### Run tests by marker:
```bash
# Run only regression tests
pytest -m regression

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Run with coverage report:
```bash
pytest --cov=api tests/
```

### Run and generate HTML coverage report:
```bash
pytest --cov=api --cov-report=html tests/
# Open htmlcov/index.html in browser
```

## Test Organization

- `test_regression.py` - Tests for known bugs to prevent regression
  - October 2, 2025 children formatting bug
  - Article numbering consistency
  - Age calculation edge cases

- `test_poa_generator.py` - Unit tests for Power of Attorney generator
  - Document generation
  - Pronoun handling
  - Required content verification

- `conftest.py` - Shared fixtures and test data
- `fixtures/` - Test data files and expected outputs

## Test Markers

Tests are organized with markers for selective running:

- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests (full document generation)
- `@pytest.mark.slow` - Tests that take longer to run

## Writing New Tests

When adding new generators or fixing bugs:

1. **Add regression test** for the bug to prevent recurrence
2. **Add unit tests** for new functions
3. **Add integration test** for complete document generation
4. **Use fixtures** from conftest.py for consistent test data

## Continuous Integration

These tests should be run:
- Before committing changes
- Before deploying to production
- Automatically in CI/CD pipeline (future enhancement)

## Test Coverage Goals

Target: 80%+ coverage for critical modules
- generate-will.py: High priority (most complex)
- generate-poa.py: Medium priority
- generate-hcpoa.py: Lower priority (simple)
- generate-acp.py: Lower priority (simple)
