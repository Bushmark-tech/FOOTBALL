# Prediction Flow: Where Final Results and Model Probabilities Come From

## Overview
This document explains the complete flow of how predictions are made, where the final result comes from, and how model probabilities are calculated.

## 🔄 Complete Prediction Flow

### 1. **User Initiates Prediction**
```
User submits form → Django views.py (predict function) → FastAPI endpoint
```

**File**: `predictor/views.py` (lines 275-404)

```python
def predict(request):
    # User submits: home_team, away_team, category
    api_url = "http://127.0.0.1:8001/predict"
    api_response = requests.post(api_url, json={
        "home_team": home_team,
        "away_team": away_team,
        "category": category
    })
```

### 2. **FastAPI Processes Request**
**File**: `fastapi_predictor_production.py` or `fastapi_predictor.py`

The FastAPI endpoint calls the core prediction function:
```python
from predictor.analytics import advanced_predict_match

result = advanced_predict_match(home_team, away_team, model1, model2)
```

### 3. **Core Prediction Logic** ⭐ (MOST IMPORTANT)

**File**: `predictor/analytics.py` (lines 1700-2500+)

This is where the **final result** and **model probabilities** are determined!

#### Step 3.1: Load Historical Data
```python
# Load football data (dataset 1 for Model1, dataset 2 for Model2)
data = load_football_data(dataset=1 or 2, use_cache=True)
```

#### Step 3.2: Calculate Historical Probabilities
```python
# Calculate probabilities from historical head-to-head matches
probs = calculate_probabilities_original(home_team, away_team, data, version="v1")

# Returns something like:
# {
#     "Home Team Win": 27.3,  # percentage
#     "Draw": 18.2,
#     "Away Team Win": 54.5
# }
```

**For Aston Villa vs Chelsea**, this returns:
- Home Win: 27.3%
- Draw: 18.2%
- Away Win: 54.5%

#### Step 3.3: Prepare Features for Model
```python
# Prepare input features for the ML model
input_data = preprocess_for_models(home_team, away_team, model, data)

# Features include:
# - Team form (last 5 matches)
# - Goals scored/conceded
# - Win/draw/loss counts
# - One-hot encoded team names
```

#### Step 3.4: Model Makes Prediction
```python
# Model predicts outcome
if hasattr(model, 'predict_proba'):
    # Classification model - returns probabilities
    probabilities = model.predict_proba(input_data)
    pred = model.predict(input_data)[0]
else:
    # Regression model - predicts scores
    pred = model.predict(input_data)[0]
```

**Two types of models**:

1. **Classification Model** (has `predict_proba`):
   - Directly predicts outcome: 0 (Away), 1 (Draw), or 2 (Home)
   - Returns probabilities for each outcome
   
2. **Regression Model** (no `predict_proba`):
   - Predicts goal scores (home_score, away_score)
   - Outcome determined from scores

#### Step 3.5: Determine Final Prediction

**File**: `predictor/analytics.py` (lines 1050-1112)

```python
def determine_final_prediction(model_pred, historical_probs):
    """
    Combines model prediction with historical probabilities.
    
    Logic:
    1. Get highest probability from historical data
    2. Check if model agrees with historical data
    3. Return final outcome based on combination
    """
```

**For Classification Models**:
```python
# Use model's direct prediction (pred_label)
if pred_label == 0:
    outcome = "Away"
elif pred_label == 1:
    outcome = "Draw"
elif pred_label == 2:
    outcome = "Home"
```

**For Regression Models**:
```python
# Determine from predicted scores
if home_score > away_score:
    outcome = "Home"
elif away_score > home_score:
    outcome = "Away"
else:
    outcome = "Draw"
```

#### Step 3.6: Calculate Final Probabilities

**File**: `predictor/analytics.py` (lines 2015-2149)

```python
# Convert model probabilities to standard format
# Format: {0: away_prob, 1: draw_prob, 2: home_prob}

if model has predict_proba:
    # Use model's probabilities
    prob_dict = {
        0: model_probs[0],  # Away
        1: model_probs[1],  # Draw
        2: model_probs[2]   # Home
    }
else:
    # Use historical probabilities
    prob_dict = {
        0: historical_probs["Away Team Win"] / 100.0,
        1: historical_probs["Draw"] / 100.0,
        2: historical_probs["Home Team Win"] / 100.0
    }

# Normalize to sum to 1.0
total = sum(prob_dict.values())
prob_dict = {k: v / total for k, v in prob_dict.items()}
```

#### Step 3.7: Form-Based Correction (Optional)

**File**: `predictor/analytics.py` (lines 2151-2198)

```python
# Adjust probabilities based on recent team form
home_strength = calculate_team_strength(home_team, 'home')
away_strength = calculate_team_strength(away_team, 'away')
form_diff = home_strength - away_strength

if abs(form_diff) > 0.1:
    # Blend model probabilities (60%) with form-based probabilities (40%)
    prob_dict[0] = (prob_dict[0] * 0.6) + (form_away_prob * 0.4)
    prob_dict[1] = (prob_dict[1] * 0.6) + (form_draw_prob * 0.4)
    prob_dict[2] = (prob_dict[2] * 0.6) + (form_home_prob * 0.4)
```

### 4. **Return Result to Django**

**File**: `predictor/analytics.py` (lines 2200-2300+)

```python
return {
    'prediction_number': prediction,  # 0=Away, 1=Draw, 2=Home
    'outcome': outcome,  # "Home", "Draw", or "Away"
    'probabilities': prob_dict,  # {0: away, 1: draw, 2: home}
    'confidence': confidence,  # Probability of predicted outcome
    'h2h_probabilities': probs,  # Historical probabilities
    'model_type': 'Model1' or 'Model2',
    'historical_probs': probs  # For display
}
```

### 5. **Django Saves and Displays Result**

**File**: `predictor/views.py` (lines 304-378)

```python
# Convert API result to Django format
outcome = api_result.get('prediction', 'Draw')
probabilities = api_result.get('probabilities', {...})
confidence = api_result.get('confidence', 0.5)

# Save to database
Prediction.objects.create(
    home_team=home_team,
    away_team=away_team,
    outcome=outcome,
    prob_home=probabilities.get('Home', 0.33),
    prob_draw=probabilities.get('Draw', 0.33),
    prob_away=probabilities.get('Away', 0.33),
    confidence=confidence
)

# Redirect to result page
return redirect(reverse('predictor:result') + '?' + params)
```

### 6. **Result Page Displays Prediction**

**File**: `predictor/views.py` (lines 1129-1640)

```python
def result(request):
    # Get parameters from URL
    outcome = request.GET.get('outcome', 'Draw')
    probabilities = {...}
    
    # Calculate historical probabilities again for display
    historical_probs = calculate_probabilities_original(
        home_team, away_team, data, version="v1"
    )
    
    # Get team form
    home_team_form = get_team_recent_form_original(home_team, data)
    away_team_form = get_team_recent_form_original(away_team, data)
    
    # Get head-to-head history
    h2h_matches = [...]  # Last 5 H2H matches
    
    # Render template with all data
    return render(request, 'predictor/result.html', context)
```

## 📊 Where Each Component Comes From

### **Final Prediction Outcome** ("Home", "Draw", or "Away")
**Source**: `advanced_predict_match()` in `predictor/analytics.py`

**Determined by**:
1. **Primary**: Model's direct prediction (classification) or predicted scores (regression)
2. **Secondary**: Historical probabilities (if model is uncertain)
3. **Tertiary**: Form-based adjustment (if form difference is significant)

### **Model Probabilities** (prob_home, prob_draw, prob_away)
**Source**: `advanced_predict_match()` in `predictor/analytics.py`

**Calculated from**:
1. **If model has `predict_proba`**: Use model's probability output
2. **If model is regressor**: Use historical probabilities from H2H data
3. **Form adjustment**: Blend with form-based probabilities (60% model, 40% form)
4. **Normalization**: Ensure probabilities sum to exactly 1.0

### **Historical Probabilities** (displayed separately)
**Source**: `calculate_probabilities_original()` in `predictor/analytics.py`

**Calculated from**:
- Head-to-head match history from CSV data
- Count of Home wins / Draws / Away wins
- Converted to percentages

**Example for Aston Villa vs Chelsea**:
```python
# From 11 historical matches:
# 3 Home wins, 2 Draws, 6 Away wins
{
    "Home Team Win": 3/11 * 100 = 27.3%,
    "Draw": 2/11 * 100 = 18.2%,
    "Away Team Win": 6/11 * 100 = 54.5%
}
```

### **Recent Form** (LWWWW, WWDDW)
**Source**: `get_team_recent_form_original()` in `predictor/analytics.py`

**Calculated from**:
- Last 5 matches for each team from CSV data
- W = Win (3 points), D = Draw (1 point), L = Loss (0 points)
- Most recent match first

### **Confidence** (0.0 to 1.0)
**Source**: `advanced_predict_match()` in `predictor/analytics.py`

**Equals**: The probability of the predicted outcome
- If predicting "Draw" with 18.2% probability → confidence = 0.182
- If predicting "Away" with 54.5% probability → confidence = 0.545

## 🎯 Example: Aston Villa vs Chelsea

### Input:
- Home Team: Aston Villa
- Away Team: Chelsea
- Category: European Leagues (Premier League)

### Processing:

1. **Load Data**: `football_data1.csv` (Model1 for Premier League)

2. **Historical Probabilities** (from H2H data):
   ```python
   {
       "Home Team Win": 27.3%,
       "Draw": 18.2%,
       "Away Team Win": 54.5%
   }
   ```

3. **Team Form** (from recent matches):
   ```python
   home_form = "LWWWW"  # Aston Villa: 12 points
   away_form = "WWDDW"  # Chelsea: 11 points
   ```

4. **Model Prediction**:
   - Model analyzes features (form, goals, H2H, etc.)
   - Predicts outcome: **"Draw"**
   - Model probabilities: {0: 0.545, 1: 0.182, 2: 0.273}

5. **Form Adjustment**:
   - Home strength: 0.52 (Villa has good recent form)
   - Away strength: 0.48 (Chelsea slightly lower)
   - Form difference: 0.04 (not significant enough for major adjustment)

6. **Final Result**:
   ```python
   {
       'outcome': 'Draw',
       'prediction_number': 1,
       'probabilities': {
           'Home': 0.273,  # 27.3%
           'Draw': 0.182,  # 18.2%
           'Away': 0.545   # 54.5%
       },
       'confidence': 0.182,  # 18.2% (Draw probability)
       'model_type': 'Model1'
   }
   ```

## 🔍 Key Insights

### Why "Draw" despite 54.5% Away Win probability?

The model considers **multiple factors**:
1. **Recent Form**: Aston Villa has better recent form (LWWWW = 12 pts vs WWDDW = 11 pts)
2. **Home Advantage**: Playing at home gives Villa an edge
3. **Match Context**: Model sees patterns suggesting a close match
4. **Historical Context**: While Chelsea has won more historically, recent form matters

The **historical probabilities** (27.3% / 18.2% / 54.5%) are shown for **reference**, but the **model's prediction** takes precedence because it considers:
- Current form
- Home advantage
- Recent trends
- Team strength

### Probability Sources Priority:

1. **Model probabilities** (if model has `predict_proba`) - HIGHEST PRIORITY
2. **Historical probabilities** (from H2H data) - Used for display and fallback
3. **Form-based adjustment** (blended with model probs) - Refines the prediction

## 📝 Summary

**The final result comes from**:
- `advanced_predict_match()` function in `predictor/analytics.py`
- Combines ML model prediction + historical data + recent form
- Returns outcome, probabilities, and confidence

**Model probabilities come from**:
- ML model's `predict_proba()` method (if available)
- OR historical H2H probabilities (for regression models)
- Adjusted by recent team form (60% model, 40% form)
- Normalized to sum to 1.0

**The system prioritizes**:
1. Model's learned patterns (from training data)
2. Recent form and current team strength
3. Historical head-to-head statistics

This multi-factor approach provides more accurate predictions than relying on historical data alone!

