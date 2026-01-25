# Football Prediction System - Complete Code Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Core Components](#core-components)
4. [Parameters & Configuration](#parameters--configuration)
5. [Data Flow](#data-flow)
6. [Design Decisions & Rationale](#design-decisions--rationale)

---

## System Overview

This is a professional football match prediction system built using Django, implementing advanced software design patterns and machine learning models to predict match outcomes with high accuracy.

### Key Features
- **Dual-Model Architecture**: Model1 for European leagues (one-hot encoding), Model2 for other leagues (team ID-based)
- **Strategy Pattern**: Multiple probability calculation strategies (Historical H2H, Form-Based, Blended)
- **Builder Pattern**: Structured prediction result construction with validation
- **Factory Pattern**: Automatic model selection based on team categories
- **Chain of Responsibility**: Team name matching with multiple fallback strategies
- **Repository Pattern**: Centralized data access and caching

---

## Architecture & Design Patterns

### 1. **Builder Pattern** (`builders.py`)

**Purpose**: Construct complex prediction results step-by-step with validation.

#### `PredictionResultBuilder`

**Why**: Ensures prediction results are always valid and complete before being used. Prevents runtime errors from missing or invalid data.

```python
class PredictionResultBuilder:
    """Builds and validates prediction results"""
```

**Key Methods**:

##### `set_prediction(prediction_number, outcome)`
- **Parameters**:
  - `prediction_number` (int): Numeric prediction (0=Away, 1=Draw, 2=Home)
  - `outcome` (str): Human-readable outcome ("Home", "Draw", "Away", or double chance like "1X")
- **Why**: Separates machine format (numbers) from user-friendly format (strings)
- **Validation**: Ensures prediction_number is in [0, 1, 2]

##### `set_probabilities(prob_dict)`
- **Parameters**:
  - `prob_dict` (dict): `{0: away_prob, 1: draw_prob, 2: home_prob}`
- **Why**: Standardizes probability format across different models
- **Validation**:
  - All probabilities must be in [0, 1] range
  - Automatically converts percentages (0-100) to decimals
  - Renormalizes if sum ≠ 1.0 (allows for floating-point errors within 5%)
  - Accepts string keys and converts to int

##### `set_confidence(confidence)`
- **Parameters**:
  - `confidence` (float): Model confidence level [0, 1]
- **Why**: Indicates how certain the model is about its prediction
- **Validation**: Must be in [0, 1] range

##### `set_model_info(model_type, model_prediction, model_probs)`
- **Parameters**:
  - `model_type` (str): "Model1" or "Model2"
  - `model_prediction`: Raw model prediction
  - `model_probs`: Raw model probabilities
- **Why**: Tracks which model made the prediction for debugging and analytics
- **Effect**: Sets model-specific fields, nullifies the other model's fields

##### `add_h2h_data(h2h_probabilities)`
- **Parameters**:
  - `h2h_probabilities` (dict): Head-to-head probability data
- **Why**: Optional enrichment with historical matchup data

##### `build()`
- **Returns**: Complete, validated prediction dictionary
- **Why**: Final validation step before returning result
- **Fallback**: Provides sensible defaults if required fields are missing (prevents crashes)
- **Required Fields**: `prediction_number`, `outcome`, `probabilities`, `confidence`, `model_type`

---

### 2. **Factory Pattern** (`factory.py`)

**Purpose**: Automatically select the correct predictor based on team characteristics.

#### Base Class: `Predictor` (Abstract)

**Why**: Defines contract that all predictors must follow (polymorphism).

**Abstract Methods**:
- `preprocess(home_team, away_team, data, adapter)`: Prepare features
- `predict(features)`: Get prediction and probabilities
- `get_model_type()`: Return model identifier

---

#### `Model1Predictor`

**For**: European leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)

**Why**: These leagues have consistent team names and rich historical data. One-hot encoding works well because:
- Fixed set of teams (20-22 teams per league)
- Stable team identities over seasons
- Rich feature space from encoded team names

**Parameters**:
- `model`: Pre-trained scikit-learn model with one-hot encoding

**How It Works**:
1. **Preprocessing**: Calls `preprocess_for_models()` which creates one-hot encoded features
2. **Prediction**: Uses `predict_proba()` to get class probabilities
3. **Probability Mapping**: Maps model classes to standard format (0=Away, 1=Draw, 2=Home)

**Class Mapping Logic**:
```python
# Handles various class label formats:
# - Numeric: 0, 1, 2
# - String: 'A', 'D', 'H'
# - Full words: 'AWAY', 'DRAW', 'HOME'
```

---

#### `Model2Predictor`

**For**: Other leagues (MLS, J-League, etc.) and teams not in European top 5

**Why**: These leagues have:
- More team turnover (promotion/relegation, new franchises)
- Less historical data
- Team IDs provide better generalization than one-hot encoding

**Parameters**:
- `model`: Pre-trained model using team ID features
- `team_mapping`: Dictionary mapping team names to numeric IDs

**How It Works**:
1. **Preprocessing**: Uses team IDs from `team_mapping.csv`
2. **Prediction**: 
   - Classifier: Uses `predict_proba()` for probabilities
   - Regressor: Predicts total goals (converted to outcome)
3. **Fallback**: Returns empty dict `{}` for regressors (handled upstream)

---

#### `ModelFactory`

**Purpose**: Intelligent model selection based on team categories.

**Parameters**:
- `team_categories` (dict): `{'main_teams': [...], 'other_teams': [...]}`

**Selection Priority**:

1. **Explicit Category** (if provided):
   - `'European Leagues'` → Model1
   - Anything else → Model2

2. **Team Category Matching**:
   - Both teams in `main_teams` → Model1
   - Both teams in `other_teams` → Model2
   - Mixed or unknown → Model2 (safer fallback)

**Why This Approach**:
- **Explicit category**: User knows the league context
- **Team matching**: Automatic detection when category not provided
- **Fallback to Model2**: More robust for unknown teams (team IDs generalize better)

---

### 3. **Strategy Pattern** (`strategies.py`)

**Purpose**: Multiple algorithms for calculating match probabilities, selected at runtime.

#### Base Class: `ProbabilityCalculator` (Abstract)

**Abstract Methods**:
- `calculate(home_team, away_team, data, adapter)`: Returns probability dict
- `get_strategy_name()`: Returns strategy identifier

---

#### `HistoricalH2HCalculator`

**Strategy**: Pure head-to-head historical data

**Why**: Historical matchups are the strongest predictor when available.

**Parameters** (in `calculate`):
- `home_team` (str): Home team name
- `away_team` (str): Away team name
- `data` (DataFrame): Historical match data
- `adapter`: Data format adapter (v1/v2)

**Algorithm**:
1. **Find H2H Matches**: Filter data for matches between these two teams
2. **Bidirectional Analysis**:
   - Direction 1: home_team as HOME vs away_team as AWAY
   - Direction 2: home_team as AWAY vs away_team as HOME (flipped)
3. **Weighted Calculation**:
   - Home matches: weight = 1.0 (most relevant)
   - Away matches: weight = 0.6 (accounts for home advantage)
4. **Result Flipping**: When home team was away, flip results:
   - Their home win → Our away win
   - Their away win → Our home win
   - Draw → Draw

**Minimum Data Requirement**: At least 1 H2H match (returns None otherwise)

**Why Weighting**:
- Home advantage is real in football (~40-45% home win rate vs ~30% away)
- Recent matches at the same venue are more predictive
- Prevents identical probabilities for reversed fixtures (Man City vs Liverpool ≠ Liverpool vs Man City)

---

#### `FormBasedCalculator`

**Strategy**: Based on recent team form (last 5 matches)

**Why**: Current form often matters more than distant history.

**Parameters** (in `calculate`):
- Same as HistoricalH2HCalculator

**Algorithm**:
1. **Get Recent Form**: Last 5 matches for each team
2. **Calculate Form Scores**:
   - Win = 3 points
   - Draw = 1 point
   - Loss = 0 points
3. **Strength Calculation**:
   ```python
   home_strength = home_points / 15.0  # Max 15 points (5 wins)
   away_strength = away_points / 15.0
   strength_diff = home_strength - away_strength
   ```
4. **Probability Mapping**:
   - Very close (`|diff| < 0.03`): 33/34/33 (even)
   - Strong home (`diff > 0.20`): 58/24/18 (home favored)
   - Strong away (`diff < -0.20`): 18/24/58 (away favored)
   - Gradual scaling for intermediate differences

**Why This Mapping**:
- Based on real-world football statistics
- Accounts for draw probability (~25-30% in professional football)
- Home advantage built into baseline (home slightly favored when even)

---

#### `BlendedCalculator`

**Strategy**: Combines multiple calculators with weights

**Why**: Ensemble methods often outperform single strategies.

**Parameters**:
- `calculators` (list): List of ProbabilityCalculator instances
- `weights` (list): Corresponding weights (must sum to 1.0)

**Algorithm**:
1. **Execute All Calculators**: Get probabilities from each
2. **Weighted Average**:
   ```python
   final_prob = Σ(calculator_prob * weight) / Σ(weights_of_successful_calculators)
   ```
3. **Skip Failed Calculators**: If a calculator returns None, exclude it and renormalize weights

**Example Configuration**:
```python
BlendedCalculator(
    calculators=[HistoricalH2HCalculator(), FormBasedCalculator()],
    weights=[0.7, 0.3]  # 70% H2H, 30% form
)
```

**Why**:
- H2H is most reliable when available (high weight)
- Form provides context for current team state (lower weight)
- Graceful degradation if H2H data unavailable

---

### 4. **Chain of Responsibility** (`matchers.py`)

**Purpose**: Try multiple team name matching strategies until one succeeds.

**Why**: Team names vary across datasets:
- "Man City" vs "Manchester City"
- "Man Utd" vs "Manchester United"
- "PSG" vs "Paris Saint-Germain"

**Chain Order** (most specific to most general):
1. **ExactMatcher**: Exact string match (fastest)
2. **NormalizedMatcher**: Normalized names (handles case, spaces, special chars)
3. **AliasMatcher**: Common aliases (Man City → Manchester City)
4. **FuzzyMatcher**: Fuzzy string matching (Levenshtein distance)
5. **IDMatcher**: Team ID lookup from mapping file

**Why This Order**:
- Fast path first (exact match)
- Progressively more expensive operations
- Stops at first successful match

---

### 5. **Repository Pattern** (`repositories.py`)

**Purpose**: Centralized data access with caching.

**Why**: 
- Separates data access from business logic
- Enables caching to reduce file I/O
- Makes testing easier (can mock repository)

#### `DataRepository`

**Key Methods**:

##### `get_football_data(version='v2', force_reload=False)`
- **Parameters**:
  - `version` (str): 'v1' or 'v2' (data format)
  - `force_reload` (bool): Bypass cache
- **Returns**: DataFrame with historical match data
- **Caching**: In-memory cache with 5-minute TTL
- **Why**: Football data rarely changes, caching reduces disk reads

##### `get_team_mapping(force_reload=False)`
- **Returns**: Dictionary mapping team names to IDs
- **Caching**: In-memory cache
- **Why**: Team mapping is static, perfect for caching

##### `get_team_categories(force_reload=False)`
- **Returns**: `{'main_teams': [...], 'other_teams': [...]}`
- **Caching**: In-memory cache
- **Why**: Team categories computed once, reused many times

---

## Parameters & Configuration

### Model Parameters

#### Model1 (European Leagues)
```python
# Feature Engineering
- One-hot encoding for team names
- Home/Away indicators
- Recent form (last 5 matches)
- Goals scored/conceded averages
- Win/Draw/Loss percentages

# Model Type: RandomForestClassifier
# Classes: 0 (Away), 1 (Draw), 2 (Home)
```

#### Model2 (Other Leagues)
```python
# Feature Engineering
- Team IDs from mapping file
- Home/Away indicators
- Recent form
- Goals statistics
- League-specific features

# Model Type: RandomForestClassifier or Regressor
# Classes: Same as Model1 (if classifier)
```

---

### Probability Calculation Parameters

#### H2H Weighting
```python
HOME_MATCH_WEIGHT = 1.0   # Matches at same venue
AWAY_MATCH_WEIGHT = 0.6   # Reversed fixtures
```

**Why 0.6**: 
- Balances historical context with venue importance
- Prevents over-weighting of limited data
- Empirically tested to produce realistic probabilities

#### Form-Based Thresholds
```python
VERY_CLOSE_THRESHOLD = 0.03   # ±3% strength difference
CLOSE_THRESHOLD = 0.08        # ±8% strength difference
MODERATE_THRESHOLD = 0.12     # ±12% strength difference
STRONG_THRESHOLD = 0.20       # ±20% strength difference
```

**Why These Values**:
- Based on analysis of real match outcomes
- Gradual scaling prevents sharp probability jumps
- Accounts for football's inherent unpredictability

---

### Validation Parameters

#### Probability Validation
```python
MIN_PROBABILITY = 0.0
MAX_PROBABILITY = 1.01  # Allows 1% floating-point error
SUM_TOLERANCE = 0.05    # 5% tolerance for probability sum
```

#### Confidence Thresholds
```python
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.01
```

---

## Data Flow

### Prediction Request Flow

```
1. User Request
   ↓
2. View Layer (views.py)
   ↓
3. Repository: Load Data & Models
   ↓
4. Factory: Select Predictor (Model1 or Model2)
   ↓
5. Predictor: Preprocess Features
   ↓
6. Predictor: Generate Prediction & Probabilities
   ↓
7. Strategy: Calculate H2H/Form Probabilities
   ↓
8. Builder: Construct Result
   ↓
9. Builder: Validate Result
   ↓
10. Return to View
   ↓
11. Render to User
```

### Data Loading Flow

```
1. Request Data
   ↓
2. Check Cache
   ├─ Hit: Return Cached Data
   └─ Miss:
      ↓
      3. Load from File
      ↓
      4. Parse & Validate
      ↓
      5. Store in Cache
      ↓
      6. Return Data
```

---

## Design Decisions & Rationale

### Why Dual-Model Architecture?

**Problem**: Different leagues have different characteristics.

**Solution**: 
- **Model1**: Optimized for stable, data-rich European leagues
- **Model2**: Generalized for diverse, data-sparse leagues

**Benefits**:
- Higher accuracy for European matches (Model1 specialization)
- Better coverage for global leagues (Model2 robustness)
- Automatic selection prevents user error

---

### Why Builder Pattern for Results?

**Problem**: Prediction results have many fields, easy to miss required data.

**Solution**: Step-by-step construction with validation.

**Benefits**:
- Compile-time safety (can't forget required fields)
- Runtime validation (catches invalid data)
- Graceful degradation (fallback values prevent crashes)
- Clear error messages for debugging

---

### Why Strategy Pattern for Probabilities?

**Problem**: Different situations require different calculation methods.

**Solution**: Pluggable strategies selected at runtime.

**Benefits**:
- Easy to add new strategies (Open/Closed Principle)
- Can combine strategies (BlendedCalculator)
- Testable in isolation
- Clear separation of concerns

---

### Why Chain of Responsibility for Team Matching?

**Problem**: Team names vary across datasets and user input.

**Solution**: Try multiple matching strategies in order.

**Benefits**:
- Handles all name variations
- Fast path for common cases (exact match)
- Extensible (add new matchers easily)
- Fails gracefully (returns None if no match)

---

### Why Repository Pattern for Data Access?

**Problem**: Data loading scattered across codebase, no caching.

**Solution**: Centralized data access with built-in caching.

**Benefits**:
- Single source of truth for data
- Automatic caching reduces I/O
- Easy to swap data sources (file → database)
- Testable (can mock repository)

---

### Why Weighted H2H Probabilities?

**Problem**: Home advantage is real, but naive H2H treats all matches equally.

**Solution**: Weight home matches higher than away matches.

**Example**:
```
Liverpool vs Man City at Anfield:
- 3 matches at Anfield: Liverpool 2-1-0 (67% win rate)
- 3 matches at Etihad: Liverpool 0-1-2 (0% win rate)

Naive: 2+0 / 6 = 33% Liverpool win
Weighted: (2*1.0 + 0*0.6) / (3*1.0 + 3*0.6) = 2/4.8 = 42% Liverpool win
```

**Why**: Venue matters in football, weighting reflects this reality.

---

### Why Fallback to Form-Based Probabilities?

**Problem**: New matchups have no H2H data.

**Solution**: Use recent form as proxy for team strength.

**Benefits**:
- Always provides a prediction (never fails)
- Form is often more relevant than distant history
- Accounts for current team state (injuries, transfers, etc.)

---

### Why Normalize Team Names?

**Problem**: User input varies ("man city", "Man City", "Manchester City").

**Solution**: Normalize to standard format before matching.

**Normalization Steps**:
1. Convert to lowercase
2. Remove special characters
3. Standardize spaces
4. Apply common aliases

**Benefits**:
- Robust to user input variations
- Consistent database lookups
- Reduces matching errors

---

### Why Separate Model Info in Builder?

**Problem**: Need to track which model made prediction for debugging.

**Solution**: `set_model_info()` stores model type and raw outputs.

**Benefits**:
- Debugging: Can trace predictions back to specific model
- Analytics: Track model performance over time
- Transparency: Users can see which model was used

---

### Why Auto-Detect Data Version?

**Problem**: System must handle both v1 and v2 data formats.

**Solution**: Check column names to detect format automatically.

**Detection Logic**:
```python
if 'Home' in columns and 'Away' in columns:
    version = 'v2'
elif 'HomeTeam' in columns and 'AwayTeam' in columns:
    version = 'v1'
```

**Benefits**:
- Works with both old and new data
- No manual configuration needed
- Prevents format mismatch errors

---

### Why Renormalize Probabilities?

**Problem**: Floating-point arithmetic can cause probabilities to sum to 0.999 or 1.001.

**Solution**: If sum deviates from 1.0 by >5%, renormalize.

**Example**:
```python
probs = {0: 0.35, 1: 0.33, 2: 0.33}  # Sum = 1.01
# Renormalize:
total = 1.01
probs = {0: 0.35/1.01, 1: 0.33/1.01, 2: 0.33/1.01}  # Sum = 1.0
```

**Benefits**:
- Prevents downstream errors
- Maintains mathematical validity
- Tolerates minor floating-point errors

---

## Error Handling & Robustness

### Graceful Degradation

**Philosophy**: Never crash, always provide a prediction.

**Fallback Chain**:
1. Try Model1/Model2 prediction
2. If fails, try H2H probabilities
3. If fails, try form-based probabilities
4. If fails, use default probabilities (40/30/30)

**Why**: Better to give a reasonable guess than to crash.

---

### Validation at Every Step

**Builder Validation**:
- Prediction number in valid range
- Probabilities sum to ~1.0
- Confidence in [0, 1]
- Required fields present

**Data Validation**:
- Check for None/empty DataFrames
- Verify column existence
- Handle missing values
- Type checking (str vs int vs float)

**Why**: Catch errors early, provide clear error messages.

---

### Logging Strategy

**Log Levels**:
- `INFO`: Normal operations (model selection, H2H matches found)
- `WARNING`: Recoverable issues (team not found, using fallback)
- `ERROR`: Serious issues (model prediction failed)

**What to Log**:
- Model selection decisions
- Team matching results
- H2H match counts
- Fallback triggers
- Validation errors

**Why**: Essential for debugging production issues.

---

## Performance Optimizations

### Caching Strategy

**What to Cache**:
- Football data (5-minute TTL)
- Team mapping (no expiration)
- Team categories (no expiration)

**Why**:
- Data rarely changes
- File I/O is expensive
- Multiple requests for same data

---

### Vectorized Operations

**Where**: Probability calculations in `analytics.py`

**Example**:
```python
# Slow (iterative):
for row in data:
    if row['Home'] == home_team:
        count += 1

# Fast (vectorized):
count = (data['Home'] == home_team).sum()
```

**Why**: Pandas vectorized operations are 10-100x faster.

---

### Lazy Imports

**Where**: `analytics.py` imports pandas/numpy lazily

**Why**:
- Faster startup time
- Can detect corrupted packages
- Only import when needed

---

## Testing Recommendations

### Unit Tests

**What to Test**:
- Builder validation logic
- Probability calculations
- Team name matching
- Model selection logic

**Example**:
```python
def test_builder_validates_probabilities():
    builder = PredictionResultBuilder()
    builder.set_probabilities({0: 0.5, 1: 0.3, 2: 0.3})  # Sum > 1
    result = builder.build()
    assert abs(sum(result['probabilities'].values()) - 1.0) < 0.01
```

---

### Integration Tests

**What to Test**:
- End-to-end prediction flow
- Data loading and caching
- Model prediction accuracy
- Fallback mechanisms

---

### Edge Cases to Test

1. **No H2H data**: Should fall back to form
2. **New teams**: Should use Model2
3. **Invalid team names**: Should handle gracefully
4. **Empty data**: Should use default probabilities
5. **Corrupted model**: Should log error and use fallback

---

## Maintenance & Extension

### Adding a New Probability Strategy

1. Create class inheriting from `ProbabilityCalculator`
2. Implement `calculate()` method
3. Implement `get_strategy_name()` method
4. Add to BlendedCalculator if desired

**Example**:
```python
class RecentFormCalculator(ProbabilityCalculator):
    def calculate(self, home_team, away_team, data, adapter):
        # Your logic here
        return {"Home Team Win": ..., "Draw": ..., "Away Team Win": ...}
    
    def get_strategy_name(self):
        return "RecentForm"
```

---

### Adding a New Model

1. Create predictor class inheriting from `Predictor`
2. Implement required methods
3. Update `ModelFactory` selection logic
4. Train and save model file

---

### Updating Team Categories

**File**: `team_categories.json` or database

**Format**:
```json
{
    "main_teams": ["Arsenal", "Chelsea", ...],
    "other_teams": ["Seattle Sounders", ...]
}
```

**Why**: Centralized configuration, easy to update.

---

## Conclusion

This system demonstrates professional software engineering practices:

- **Design Patterns**: Builder, Factory, Strategy, Chain of Responsibility, Repository
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Robustness**: Validation, fallbacks, error handling
- **Performance**: Caching, vectorization, lazy loading
- **Maintainability**: Clear separation of concerns, extensible architecture

The architecture is designed to be:
- **Accurate**: Dual models optimized for different leagues
- **Robust**: Multiple fallback strategies
- **Fast**: Caching and vectorized operations
- **Maintainable**: Clear patterns and separation of concerns
- **Extensible**: Easy to add new models, strategies, and features

---

**Last Updated**: 2026-01-11
**Version**: 1.0
**Author**: Football Prediction System Team
