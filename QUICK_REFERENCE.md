# Quick Reference Guide - Football Prediction System

## Quick Start

### Making a Prediction

```python
from predictor.factory import ModelFactory
from predictor.builders import PredictionResultBuilder
from predictor.repositories import get_repository

# 1. Load data and models
repo = get_repository()
data = repo.get_football_data(version='v2')
model1 = repo.get_model('model1')
model2 = repo.get_model('model2')
team_mapping = repo.get_team_mapping()
team_categories = repo.get_team_categories()

# 2. Create factory and get predictor
factory = ModelFactory(team_categories)
predictor = factory.create_predictor(
    home_team="Arsenal",
    away_team="Chelsea",
    model1=model1,
    model2=model2,
    team_mapping=team_mapping,
    category="European Leagues"  # Optional
)

# 3. Preprocess and predict
features = predictor.preprocess("Arsenal", "Chelsea", data, adapter)
prediction, probabilities = predictor.predict(features)

# 4. Build result
builder = PredictionResultBuilder()
result = (builder
    .set_prediction(prediction, "Home")
    .set_probabilities(probabilities)
    .set_confidence(0.75)
    .set_model_info(predictor.get_model_type(), prediction, probabilities)
    .build())
```

---

## Parameter Quick Reference

### Prediction Numbers
```python
0 = Away Win
1 = Draw
2 = Home Win
```

### Outcome Strings
```python
"Home"      # Home team wins
"Draw"      # Match draws
"Away"      # Away team wins
"1X"        # Home or Draw (double chance)
"X2"        # Draw or Away (double chance)
"12"        # Home or Away (no draw)
```

### Model Types
```python
"Model1"    # European leagues (one-hot encoding)
"Model2"    # Other leagues (team IDs)
```

### Data Versions
```python
"v1"        # Old format: HomeTeam, AwayTeam, FTR
"v2"        # New format: Home, Away, Res
```

---

## Common Patterns

### Pattern 1: Calculate H2H Probabilities

```python
from predictor.strategies import HistoricalH2HCalculator

calculator = HistoricalH2HCalculator()
probs = calculator.calculate(
    home_team="Liverpool",
    away_team="Man City",
    data=data,
    adapter=adapter
)
# Returns: {"Home Team Win": 45.0, "Draw": 30.0, "Away Team Win": 25.0}
# Or None if no H2H data
```

### Pattern 2: Calculate Form-Based Probabilities

```python
from predictor.strategies import FormBasedCalculator

calculator = FormBasedCalculator()
probs = calculator.calculate(
    home_team="Liverpool",
    away_team="Man City",
    data=data,
    adapter=adapter
)
# Always returns probabilities (never None)
```

### Pattern 3: Blend Multiple Strategies

```python
from predictor.strategies import BlendedCalculator, HistoricalH2HCalculator, FormBasedCalculator

calculator = BlendedCalculator(
    calculators=[HistoricalH2HCalculator(), FormBasedCalculator()],
    weights=[0.7, 0.3]  # 70% H2H, 30% form
)
probs = calculator.calculate(home_team, away_team, data, adapter)
```

### Pattern 4: Match Team Names

```python
from predictor.matchers import get_team_matcher_chain

matcher = get_team_matcher_chain()
team_mapping = load_team_mapping()

# Find "Man City" in dataset
actual_name = matcher.match(
    "Man City",
    unique_teams=data['Home'].unique(),
    team_mapping=team_mapping
)
# Returns: "Manchester City" or None
```

### Pattern 5: Load Data with Caching

```python
from predictor.repositories import get_repository

repo = get_repository()

# First call: loads from file
data = repo.get_football_data(version='v2')

# Second call: returns cached data (fast)
data = repo.get_football_data(version='v2')

# Force reload (bypass cache)
data = repo.get_football_data(version='v2', force_reload=True)
```

---

## Validation Rules

### Probabilities
```python
# Valid
{0: 0.35, 1: 0.30, 2: 0.35}  # Sum = 1.0
{0: 35, 1: 30, 2: 35}        # Percentages (auto-converted)
{0: 0.34, 1: 0.33, 2: 0.34}  # Sum = 1.01 (auto-normalized)

# Invalid
{0: 1.5, 1: 0.3, 2: 0.2}     # Value > 1.0
{0: 0.5, 1: 0.2, 2: 0.1}     # Sum = 0.8 (too far from 1.0)
```

### Confidence
```python
# Valid
0.75    # 75% confident
0.0     # No confidence
1.0     # Fully confident

# Invalid
1.5     # > 1.0
-0.1    # < 0.0
```

### Prediction Number
```python
# Valid
0, 1, 2

# Invalid
3, -1, "Home"
```

---

## Error Handling

### Handling Missing Data

```python
# Check if data is valid
if data is None or data.empty:
    # Use fallback
    probs = {"Home Team Win": 40.0, "Draw": 30.0, "Away Team Win": 30.0}
```

### Handling Failed Predictions

```python
try:
    prediction, probs = predictor.predict(features)
except Exception as e:
    logger.error(f"Prediction failed: {e}")
    # Use default values
    prediction = 1  # Draw
    probs = {0: 0.33, 1: 0.34, 2: 0.33}
```

### Handling Missing Teams

```python
from predictor.analytics import find_team_in_data

home_matched = find_team_in_data("Man City", data, "Home")
if home_matched is None:
    # Team not found, use fallback strategy
    logger.warning(f"Team not found: Man City")
```

---

## Configuration

### Team Categories File

**Location**: `data/team_categories.json`

```json
{
    "main_teams": [
        "Arsenal", "Chelsea", "Liverpool", "Man City",
        "Barcelona", "Real Madrid", "Bayern Munich"
    ],
    "other_teams": [
        "Seattle Sounders", "LA Galaxy", "Kashima Antlers"
    ]
}
```

### Team Mapping File

**Location**: `data/team_mapping.csv`

```csv
team_name,team_id
Arsenal,1
Chelsea,2
Liverpool,3
Man City,4
```

### Data Files

**Location**: `data/`

- `football_data1.csv` - v1 format (old)
- `football_data2.csv` - v2 format (new)

---

## Logging

### Log Levels

```python
import logging

logger = logging.getLogger(__name__)

# Normal operations
logger.info("Using Model1 for European League match")

# Recoverable issues
logger.warning("Team not found, using fallback")

# Serious issues
logger.error("Model prediction failed")
```

### What to Log

```python
# Model selection
logger.info(f"Using {model_type} for {home} vs {away}")

# H2H data
logger.info(f"Found {count} H2H matches")

# Fallbacks
logger.warning(f"No H2H data, using form-based probabilities")

# Errors
logger.error(f"Prediction failed: {error}")
```

---

## Performance Tips

### 1. Use Caching

```python
# Good: Uses cache
repo = get_repository()
data = repo.get_football_data()

# Bad: Loads from file every time
data = pd.read_csv('data/football_data2.csv')
```

### 2. Vectorize Operations

```python
# Good: Vectorized
home_matches = data[data['Home'] == 'Arsenal']

# Bad: Iterative
home_matches = []
for row in data.iterrows():
    if row['Home'] == 'Arsenal':
        home_matches.append(row)
```

### 3. Reuse Objects

```python
# Good: Create once, reuse
factory = ModelFactory(team_categories)
for match in matches:
    predictor = factory.create_predictor(...)

# Bad: Create every time
for match in matches:
    factory = ModelFactory(team_categories)
    predictor = factory.create_predictor(...)
```

---

## Testing

### Unit Test Example

```python
import pytest
from predictor.builders import PredictionResultBuilder

def test_builder_validates_probabilities():
    builder = PredictionResultBuilder()
    builder.set_probabilities({0: 0.5, 1: 0.3, 2: 0.3})  # Sum > 1
    result = builder.build()
    
    # Should renormalize
    total = sum(result['probabilities'].values())
    assert abs(total - 1.0) < 0.01

def test_builder_handles_missing_fields():
    builder = PredictionResultBuilder()
    result = builder.build()  # No fields set
    
    # Should provide defaults
    assert 'prediction_number' in result
    assert 'outcome' in result
    assert result['outcome'] == 'Draw'
```

### Integration Test Example

```python
def test_end_to_end_prediction():
    # Setup
    repo = get_repository()
    data = repo.get_football_data()
    model1 = repo.get_model('model1')
    team_categories = repo.get_team_categories()
    
    # Execute
    factory = ModelFactory(team_categories)
    predictor = factory.create_predictor(
        "Arsenal", "Chelsea",
        model1, None, None,
        category="European Leagues"
    )
    
    features = predictor.preprocess("Arsenal", "Chelsea", data, adapter)
    prediction, probs = predictor.predict(features)
    
    # Verify
    assert prediction in [0, 1, 2]
    assert len(probs) == 3
    assert abs(sum(probs.values()) - 1.0) < 0.01
```

---

## Troubleshooting

### Issue: "Team not found"

**Cause**: Team name doesn't match dataset

**Solution**:
1. Check team name spelling
2. Try normalized name (lowercase, no special chars)
3. Check `team_mapping.csv` for correct name
4. Add alias to matcher chain

### Issue: "No H2H data"

**Cause**: Teams haven't played each other

**Solution**: System automatically falls back to form-based probabilities

### Issue: "Probabilities don't sum to 1.0"

**Cause**: Floating-point arithmetic

**Solution**: Builder automatically renormalizes if sum is within 5% of 1.0

### Issue: "Model prediction failed"

**Cause**: Invalid features or corrupted model

**Solution**:
1. Check feature preprocessing
2. Verify model file integrity
3. Check logs for specific error
4. Use fallback probabilities

---

## API Reference

### PredictionResultBuilder

```python
builder = PredictionResultBuilder()

# Methods (all return self for chaining)
builder.set_prediction(prediction_number: int, outcome: str)
builder.set_probabilities(prob_dict: dict)
builder.set_confidence(confidence: float)
builder.set_model_info(model_type: str, model_prediction, model_probs)
builder.add_h2h_data(h2h_probabilities: dict)
builder.add_metadata(**kwargs)

# Final method
result = builder.build()  # Returns dict
```

### ModelFactory

```python
factory = ModelFactory(team_categories: dict)

predictor = factory.create_predictor(
    home_team: str,
    away_team: str,
    model1,
    model2,
    team_mapping: dict,
    category: str = None  # Optional
)
```

### ProbabilityCalculator

```python
calculator = HistoricalH2HCalculator()  # or FormBasedCalculator, BlendedCalculator

probs = calculator.calculate(
    home_team: str,
    away_team: str,
    data: DataFrame,
    adapter
)
# Returns: dict or None
```

### DataRepository

```python
repo = get_repository()

data = repo.get_football_data(version: str = 'v2', force_reload: bool = False)
mapping = repo.get_team_mapping(force_reload: bool = False)
categories = repo.get_team_categories(force_reload: bool = False)
model = repo.get_model(model_name: str)
```

---

## Constants

```python
# Prediction outcomes
AWAY_WIN = 0
DRAW = 1
HOME_WIN = 2

# Model types
MODEL1 = "Model1"
MODEL2 = "Model2"

# Data versions
VERSION_V1 = "v1"
VERSION_V2 = "v2"

# Weighting
HOME_MATCH_WEIGHT = 1.0
AWAY_MATCH_WEIGHT = 0.6

# Thresholds
VERY_CLOSE_THRESHOLD = 0.03
CLOSE_THRESHOLD = 0.08
MODERATE_THRESHOLD = 0.12
STRONG_THRESHOLD = 0.20
```

---

## Best Practices

1. **Always use the Builder**: Don't construct result dicts manually
2. **Cache data**: Use repository, don't load files directly
3. **Log decisions**: Log model selection, fallbacks, errors
4. **Validate input**: Check team names, data availability
5. **Handle None**: All calculators can return None, check before using
6. **Use type hints**: Makes code more maintainable
7. **Write tests**: Unit tests for logic, integration tests for flow
8. **Document why**: Explain design decisions in comments

---

**Last Updated**: 2026-01-11
**Version**: 1.0
