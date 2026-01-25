# Action Checklist - Football Prediction System

**Last Updated**: 2026-01-11  
**Status**: 4/15 items completed

---

## 🔴 CRITICAL (Do Today)

### 1. Fix Corrupted Packages ⬜
**Priority**: CRITICAL  
**Time**: 10 minutes  
**Impact**: Prevents production failures

```bash
# Run these commands:
pip uninstall pandas numpy scikit-learn -y
pip cache purge
pip install --force-reinstall --no-cache-dir pandas==2.0.3 numpy==1.25.2 scikit-learn==1.6.1

# Verify installation:
python -c "import pandas; import numpy; import sklearn; print('All packages OK')"
```

**Verification**: No more package warnings when running `pip list`

---

### 2. Disable Debug Mode in Production ⬜
**Priority**: CRITICAL  
**Time**: 5 minutes  
**Impact**: Security vulnerability

**File**: `football_predictor/settings.py`

```python
# Change from:
DEBUG = True

# To:
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Also ensure:
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

**File**: `.env`
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Verification**: Check that debug toolbar doesn't appear in production

---

### 3. Remove Debug Print Statements ⬜
**Priority**: CRITICAL  
**Time**: 30 minutes  
**Impact**: Better logging, performance

**Files to Update**:
- `predictor/auth_views.py` (lines 358, 359, 377, 387, 390, 564, 565)

**Find and Replace**:
```python
# Before:
print(f"DEBUG: {message}")

# After:
logger.debug(f"{message}")
```

**Command to find all print statements**:
```bash
grep -n "print(" predictor/*.py
```

**Verification**: No `print()` statements in production code (except maybe manage.py)

---

### 4. Fix Silent Exception Handling ⬜
**Priority**: CRITICAL  
**Time**: 20 minutes  
**Impact**: Better debugging

**Files to Update**:
- `predictor/analytics.py` (lines 1978, 1982)

**Before**:
```python
except Exception: pass
```

**After**:
```python
except Exception as e:
    logger.warning(f"Failed to reconfigure encoding: {e}")
    # Continue with default encoding
```

**Verification**: Search for `except.*pass` - should find none

---

## 🟡 HIGH PRIORITY (This Week)

### 5. Add Unit Tests for Builders ⬜
**Priority**: HIGH  
**Time**: 2 hours  
**Impact**: Catch bugs early

**Create**: `tests/unit/test_builders.py`

```python
import pytest
from predictor.builders import PredictionResultBuilder

def test_builder_validates_probabilities():
    """Test that builder normalizes probabilities"""
    builder = PredictionResultBuilder()
    builder.set_probabilities({0: 0.5, 1: 0.3, 2: 0.3})
    result = builder.build()
    
    total = sum(result['probabilities'].values())
    assert abs(total - 1.0) < 0.01, f"Probabilities should sum to 1.0, got {total}"

def test_builder_handles_missing_fields():
    """Test that builder provides defaults for missing fields"""
    builder = PredictionResultBuilder()
    result = builder.build()
    
    assert 'prediction_number' in result
    assert 'outcome' in result
    assert result['outcome'] == 'Draw'

def test_builder_validates_prediction_number():
    """Test that builder validates prediction number"""
    builder = PredictionResultBuilder()
    builder.set_prediction(5, "Invalid")  # Invalid number
    result = builder.build()
    
    # Should have logged error
    assert len(builder._errors) > 0

def test_builder_converts_percentage_probabilities():
    """Test that builder converts percentages to decimals"""
    builder = PredictionResultBuilder()
    builder.set_probabilities({0: 35, 1: 30, 2: 35})  # Percentages
    result = builder.build()
    
    # Should be converted to decimals
    assert all(0 <= v <= 1 for v in result['probabilities'].values())
```

**Run**: `pytest tests/unit/test_builders.py -v`

---

### 6. Add Unit Tests for Factory ⬜
**Priority**: HIGH  
**Time**: 2 hours  
**Impact**: Ensure correct model selection

**Create**: `tests/unit/test_factory.py`

```python
import pytest
from predictor.factory import ModelFactory, Model1Predictor, Model2Predictor

@pytest.fixture
def team_categories():
    return {
        'main_teams': ['Arsenal', 'Chelsea', 'Liverpool'],
        'other_teams': ['Seattle Sounders', 'LA Galaxy']
    }

@pytest.fixture
def mock_models():
    # Create mock models for testing
    return None, None  # Replace with actual mocks

def test_factory_selects_model1_for_european_teams(team_categories, mock_models):
    """Test that factory selects Model1 for European teams"""
    factory = ModelFactory(team_categories)
    model1, model2 = mock_models
    
    predictor = factory.create_predictor(
        "Arsenal", "Chelsea",
        model1, model2, {},
        category="European Leagues"
    )
    
    assert isinstance(predictor, Model1Predictor)

def test_factory_selects_model2_for_other_teams(team_categories, mock_models):
    """Test that factory selects Model2 for other teams"""
    factory = ModelFactory(team_categories)
    model1, model2 = mock_models
    
    predictor = factory.create_predictor(
        "Seattle Sounders", "LA Galaxy",
        model1, model2, {},
        category="Others"
    )
    
    assert isinstance(predictor, Model2Predictor)

def test_factory_selects_model2_for_mixed_teams(team_categories, mock_models):
    """Test that factory defaults to Model2 for mixed teams"""
    factory = ModelFactory(team_categories)
    model1, model2 = mock_models
    
    predictor = factory.create_predictor(
        "Arsenal", "Seattle Sounders",
        model1, model2, {}
    )
    
    assert isinstance(predictor, Model2Predictor)
```

**Run**: `pytest tests/unit/test_factory.py -v`

---

### 7. Refactor Views into Service Layer ⬜
**Priority**: HIGH  
**Time**: 3-4 hours  
**Impact**: Testability, maintainability

**Create**: `predictor/services.py`

```python
import logging
from .repositories import get_repository
from .factory import ModelFactory
from .builders import PredictionResultBuilder
from .adapters import DataAdapterFactory

logger = logging.getLogger(__name__)

class PredictionService:
    """Service layer for prediction business logic"""
    
    def __init__(self, repository=None):
        self.repo = repository or get_repository()
        self.factory = ModelFactory(self.repo.get_team_categories())
    
    def make_prediction(self, home_team, away_team, category=None):
        """
        Make a prediction for a match.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            category: League category (optional)
        
        Returns:
            dict: Prediction result
        """
        try:
            # Load data and models
            data = self.repo.get_football_data(version='v2')
            model1 = self.repo.get_model('model1')
            model2 = self.repo.get_model('model2')
            team_mapping = self.repo.get_team_mapping()
            
            # Create predictor
            predictor = self.factory.create_predictor(
                home_team, away_team,
                model1, model2, team_mapping,
                category
            )
            
            # Make prediction
            adapter = DataAdapterFactory.create(version_str='v2')
            features = predictor.preprocess(home_team, away_team, data, adapter)
            prediction, probs = predictor.predict(features)
            
            # Build result
            builder = PredictionResultBuilder()
            result = (builder
                .set_prediction(prediction, self._get_outcome(prediction))
                .set_probabilities(probs)
                .set_confidence(self._calculate_confidence(probs))
                .set_model_info(predictor.get_model_type(), prediction, probs)
                .build())
            
            logger.info(f"Prediction made: {home_team} vs {away_team} = {result['outcome']}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def _get_outcome(self, prediction):
        """Convert prediction number to outcome string"""
        return {0: 'Away', 1: 'Draw', 2: 'Home'}.get(prediction, 'Draw')
    
    def _calculate_confidence(self, probs):
        """Calculate confidence from probabilities"""
        if not probs:
            return 0.5
        return max(probs.values())
```

**Update**: `predictor/views.py`

```python
# Before (in predict view):
# ... 200+ lines of prediction logic ...

# After:
from .services import PredictionService

def predict(request):
    if request.method == 'POST':
        service = PredictionService()
        try:
            result = service.make_prediction(
                home_team=request.POST['home_team'],
                away_team=request.POST['away_team'],
                category=request.POST.get('category')
            )
            # Save to database and render
            # ... (much simpler now)
        except Exception as e:
            messages.error(request, f"Prediction failed: {e}")
```

**Verification**: Views.py should be <2000 lines

---

### 8. Add Error Tracking (Sentry) ⬜
**Priority**: HIGH  
**Time**: 1 hour  
**Impact**: Catch production errors

**Step 1**: Sign up at https://sentry.io (free tier)

**Step 2**: Install SDK
```bash
pip install sentry-sdk
```

**Step 3**: Update `requirements.txt`
```
sentry-sdk>=1.40.0
```

**Step 4**: Configure in `settings.py`
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv('ENVIRONMENT', 'production'),
        release=os.getenv('GIT_COMMIT', 'unknown'),
    )
```

**Step 5**: Add to `.env`
```bash
SENTRY_DSN=your_sentry_dsn_here
ENVIRONMENT=production
```

**Verification**: Trigger a test error and see it in Sentry dashboard

---

## 🟢 MEDIUM PRIORITY (This Month)

### 9. Add Metrics Collection ⬜
**Priority**: MEDIUM  
**Time**: 3 hours

```bash
pip install django-prometheus
```

See SYSTEM_ANALYSIS_REPORT.md section 9.2 for details.

---

### 10. Add Data Validation ⬜
**Priority**: MEDIUM  
**Time**: 2 hours

Create `predictor/validators.py` - see SYSTEM_ANALYSIS_REPORT.md section 8.2

---

### 11. Add Soft Delete to Predictions ⬜
**Priority**: MEDIUM  
**Time**: 2 hours

Update `Prediction` model - see SYSTEM_ANALYSIS_REPORT.md section 6.2

---

### 12. Add API Documentation ⬜
**Priority**: MEDIUM  
**Time**: 2 hours

Add Swagger to FastAPI - see SYSTEM_ANALYSIS_REPORT.md section 10.1

---

## 🔵 LOW PRIORITY (Nice to Have)

### 13. Add Async Processing ⬜
**Priority**: LOW  
**Time**: 4-6 hours

Set up Celery for heavy operations

---

### 14. Cache Warming ⬜
**Priority**: LOW  
**Time**: 1 hour

Pre-load data on startup

---

### 15. Architecture Diagrams ⬜
**Priority**: LOW  
**Time**: 2 hours

Create Mermaid diagrams in documentation

---

## Progress Tracking

### Completed: 0/15 (0%)

```
[░░░░░░░░░░] 0%
```

### By Priority:
- 🔴 Critical: 0/4 (0%)
- 🟡 High: 0/4 (0%)
- 🟢 Medium: 0/4 (0%)
- 🔵 Low: 0/3 (0%)

---

## Quick Commands

### Run All Tests
```bash
pytest tests/ -v --cov=predictor --cov-report=html
```

### Check Code Quality
```bash
# Install tools
pip install flake8 black pylint

# Run checks
flake8 predictor/ --max-line-length=120
black predictor/ --check
pylint predictor/
```

### Find Issues
```bash
# Find print statements
grep -rn "print(" predictor/*.py

# Find silent exceptions
grep -rn "except.*pass" predictor/*.py

# Find debug code
grep -rn "DEBUG" predictor/*.py
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Notes

- Mark items as complete by changing ⬜ to ✅
- Update progress percentage as you complete items
- Add notes below each item if needed
- Refer to SYSTEM_ANALYSIS_REPORT.md for detailed instructions

---

**Next Review**: [Date after completing critical items]
