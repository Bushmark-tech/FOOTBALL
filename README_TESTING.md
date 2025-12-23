# Testing Guide for Football Predictor Pro

## 🧪 Test Suite Overview

This project includes comprehensive tests covering:
- **Model Tests**: Database models and relationships
- **View Tests**: HTTP endpoints and responses
- **Analytics Tests**: Prediction logic and calculations
- **Integration Tests**: End-to-end workflows
- **Middleware Tests**: Custom middleware functionality

## 📋 Running Tests

### Using Django Test Runner

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test predictor.tests.test_models

# Run specific test class
python manage.py test predictor.tests.test_models.PredictionModelTest

# Run specific test method
python manage.py test predictor.tests.test_models.PredictionModelTest.test_prediction_creation

# Run with verbosity
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Using pytest

```bash
# Install test requirements
pip install -r requirements_test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=predictor --cov-report=html

# Run specific test file
pytest predictor/tests/test_models.py

# Run specific test
pytest predictor/tests/test_models.py::PredictionModelTest::test_prediction_creation

# Run in parallel (faster)
pytest -n auto

# Run only fast tests (exclude slow markers)
pytest -m "not slow"
```

## 📊 Test Coverage

Current test coverage includes:

- ✅ **Models**: Prediction, Match, League, Team
- ✅ **Views**: Home, Predict, API endpoints, History
- ✅ **Analytics**: Probability calculations, prediction logic
- ✅ **Middleware**: Rate limiting, security headers, performance monitoring
- ✅ **Integration**: Complete prediction flows

## 🎯 Writing New Tests

### Test Structure

```python
from django.test import TestCase
from predictor.models import Prediction

class MyModelTest(TestCase):
    """Test cases for MyModel."""
    
    def setUp(self):
        """Set up test data."""
        # Create test data here
        pass
    
    def test_something(self):
        """Test description."""
        # Test implementation
        self.assertEqual(actual, expected)
```

### Best Practices

1. **Use descriptive test names**: `test_prediction_creation_with_valid_data`
2. **One assertion per test**: Keep tests focused
3. **Use setUp()**: Create common test data
4. **Test edge cases**: Empty data, None values, boundaries
5. **Mock external services**: Don't rely on FastAPI being running
6. **Clean up**: Django TestCase handles database cleanup automatically

## 🔍 Test Categories

### Unit Tests
- Test individual functions and methods
- Fast execution
- No external dependencies
- Example: `test_models.py`, `test_analytics.py`

### Integration Tests
- Test multiple components working together
- May require database
- Example: `test_integration.py`

### Performance Tests
- Test response times and load handling
- Use `locust` for load testing
- Example: `test_api_performance.py`

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements_test.txt
      - name: Run tests
        run: pytest --cov=predictor --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📈 Coverage Goals

- **Minimum**: 80% code coverage
- **Target**: 90% code coverage
- **Critical paths**: 100% coverage (models, views, analytics)

## 🐛 Debugging Tests

```bash
# Run with debugger
pytest --pdb

# Run with print statements
pytest -s

# Run with detailed output
pytest -vv

# Run specific failing test
pytest predictor/tests/test_models.py::TestClass::test_method -vv
```

## 📝 Test Data

- Use factories for creating test data (factory-boy)
- Use fixtures for common test scenarios
- Clean up after tests (Django handles this automatically)

## ✅ Pre-commit Testing

Before committing code:

```bash
# Run all tests
pytest

# Check code style
flake8 .
black --check .
isort --check .

# Type checking
mypy predictor/
```

---

**Note**: Always run tests before deploying to production!

