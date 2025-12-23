# Model Prediction Issue: All Matches Predicting Draw

## 🐛 Current Problem

**Every match is predicting "Draw" with identical probabilities:**
- Home: 27.8%
- Draw: 35.9%
- Away: 36.2%

### Examples:
1. **Chelsea vs Brighton**: Draw (should be Home Win - 53.8% historical)
2. **Man City vs Liverpool**: Draw (same probabilities!)
3. **Any match**: Draw (same probabilities!)

## 🔍 Root Cause Analysis

### Issue 1: Model Returns Same Probabilities
The model is returning **identical probabilities for every match**, regardless of teams:
```python
{
  "Home": 0.2784929104300466,
  "Draw": 0.35941509606197186,
  "Away": 0.3620919935079815
}
```

This indicates:
1. **Features are not team-specific** - The model receives the same input for every match
2. **Model may not be properly trained** - It's not learning team differences
3. **Feature preparation issue** - Team-specific features aren't being extracted

### Issue 2: Prediction Logic
Even though Away (36.2%) > Draw (35.9%), the system predicts "Draw" because:
1. `determine_final_prediction()` combines model + historical probabilities
2. Historical data might be overriding model probabilities
3. The difference is small (0.3%), so it might default to Draw

## 📊 What Should Happen

### For Chelsea vs Brighton:
- **Historical**: 53.8% Home, 30.8% Draw, 15.4% Away
- **Form**: Chelsea (WWDDW) > Brighton (WLDLL)
- **Expected**: Home Win (Chelsea)
- **Actual**: Draw ❌

### For Man City vs Liverpool:
- **Should have different probabilities** than Chelsea vs Brighton
- **Actual**: Same probabilities ❌

## 🔧 Solutions

### Solution 1: Fix Feature Preparation (Recommended)

The `preprocess_for_models()` function needs to extract team-specific features:

**File**: `predictor/analytics.py` (lines 1316-1500)

**Current Issue**: Features might not include:
- Team names (one-hot encoded)
- Team-specific form
- Team-specific goals scored/conceded
- Team-specific strengths

**Check**:
```python
# In advanced_predict_match(), add logging:
logger.info(f"Features for {home_team} vs {away_team}: {input_data}")
```

If features are the same for every match, that's the problem!

### Solution 2: Retrain the Model

The model might need retraining with proper features:

1. **Check training data**: `data/football_data1.csv`
2. **Verify features include**:
   - One-hot encoded team names
   - Recent form (last 5 matches)
   - Goals scored/conceded averages
   - Home advantage
   - Head-to-head history

3. **Retrain model**:
```bash
python train_model.py  # Or whatever your training script is
```

### Solution 3: Use Historical Probabilities Directly (Temporary Workaround)

Modify `advanced_predict_match()` to use historical probabilities when model probabilities are identical:

**File**: `predictor/analytics.py` (around line 2200)

```python
# After getting prob_dict from model
# Check if probabilities are suspiciously similar (model not working)
prob_values = list(prob_dict.values())
if max(prob_values) - min(prob_values) < 0.05:  # Less than 5% difference
    logger.warning("Model probabilities too similar, using historical data")
    if probs:
        # Use historical probabilities instead
        prob_dict = {
            0: probs.get("Away Team Win", 33.3) / 100.0,
            1: probs.get("Draw", 33.3) / 100.0,
            2: probs.get("Home Team Win", 33.3) / 100.0
        }
        # Normalize
        total = sum(prob_dict.values())
        prob_dict = {k: v/total for k, v in prob_dict.items()}
```

### Solution 4: Force Highest Probability Selection

Ensure the system always picks the highest probability:

**File**: `predictor/analytics.py` (line 2202)

```python
# Current code already does this:
prediction = max(prob_dict, key=prob_dict.get)

# But verify it's not being overridden by determine_final_prediction()
# Comment out lines 2239-2287 temporarily to test
```

## 🧪 Debugging Steps

### Step 1: Check Feature Values
```python
# Add to advanced_predict_match() before model.predict():
logger.info(f"Input features shape: {input_data.shape}")
logger.info(f"Input features: {input_data}")
```

### Step 2: Check Model Output
```python
# Add after model.predict_proba():
logger.info(f"Raw model probabilities: {model.predict_proba(input_data)}")
logger.info(f"Model prediction: {model.predict(input_data)}")
```

### Step 3: Test with Different Teams
```bash
# Test multiple matches
python -c "import requests; print(requests.post('http://127.0.0.1:8001/predict', json={'home_team': 'Arsenal', 'away_team': 'Tottenham'}).json())"
python -c "import requests; print(requests.post('http://127.0.0.1:8001/predict', json={'home_team': 'Barcelona', 'away_team': 'Real Madrid'}).json())"
```

If all return same probabilities → Feature preparation issue
If probabilities vary → Model working, issue is in prediction logic

## 📝 Immediate Workaround

Until the model is fixed, use historical probabilities:

**File**: `predictor/analytics.py` (line 2239)

```python
if probs:
    # TEMPORARY: Use historical probabilities directly
    prob_dict = {
        0: probs.get("Away Team Win", 33.3) / 100.0,
        1: probs.get("Draw", 33.3) / 100.0,
        2: probs.get("Home Team Win", 33.3) / 100.0
    }
    total = sum(prob_dict.values())
    if total > 0:
        prob_dict = {k: v/total for k, v in prob_dict.items()}
    
    # Get prediction from highest probability
    prediction = max(prob_dict, key=prob_dict.get)
    confidence = prob_dict[prediction]
    
    # Map to outcome
    outcome_map = {0: "Away", 1: "Draw", 2: "Home"}
    outcome = outcome_map[prediction]
    
    logger.info(f"Using historical probabilities: {prob_dict}")
    logger.info(f"Prediction: {outcome} ({prediction})")
```

This will make predictions based on historical data instead of the broken model.

## 🎯 Expected Results After Fix

### Chelsea vs Brighton:
- Probabilities: ~54% Home, ~31% Draw, ~15% Away
- Prediction: **Home Win** (Chelsea)

### Man City vs Liverpool:
- Probabilities: Different from Chelsea vs Brighton
- Prediction: Based on their specific form and history

### All Matches:
- **Different probabilities** for different teams
- Predictions based on actual team analysis

## 🚨 Priority

**HIGH PRIORITY** - The model is not functioning correctly. Every prediction is essentially random/default values.

**Action Required**:
1. Check feature preparation
2. Verify model training
3. Implement workaround using historical data
4. Retrain model with proper features

## 📚 Related Files

- `predictor/analytics.py` - Feature preparation and prediction logic
- `models/model1.pkl` - The model file (may need retraining)
- `data/football_data1.csv` - Training data
- `fastapi_predictor_production.py` - API endpoint

## ✅ Success Criteria

- [ ] Different matches return different probabilities
- [ ] Chelsea vs Brighton predicts Home Win
- [ ] Probabilities reflect team form and history
- [ ] Model considers team-specific features

