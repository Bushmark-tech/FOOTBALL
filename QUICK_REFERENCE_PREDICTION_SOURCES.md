# Quick Reference: Prediction Sources

## 🎯 One-Page Answer: Where Does Everything Come From?

### **Q: Where does the FINAL RESULT come from?**
**A: ML Model in `predictor/analytics.py` → `advanced_predict_match()` function**

- **File**: `predictor/analytics.py` (lines 1700-2500)
- **Function**: `advanced_predict_match(home_team, away_team, model1, model2)`
- **Returns**: "Home", "Draw", or "Away"
- **Based on**: ML model trained on thousands of matches + current team form + home advantage

---

### **Q: Where do MODEL PROBABILITIES come from?**
**A: Two sources depending on model type:**

#### For Classification Models (with `predict_proba`):
- **Source**: ML model's probability output
- **Function**: `model.predict_proba(features)`
- **Returns**: Probabilities for each outcome [Away, Draw, Home]

#### For Regression Models (without `predict_proba`):
- **Source**: Historical head-to-head data
- **Function**: `calculate_probabilities_original(home, away, data)`
- **File**: `predictor/analytics.py` (lines 178-225)
- **Data**: `football_data1.csv` or `football_data2.csv`
- **Calculation**: Count wins/draws/losses from past matches

**For Aston Villa vs Chelsea:**
```python
# From 11 historical matches:
# 3 Home wins → 27.3%
# 2 Draws → 18.2%
# 6 Away wins → 54.5%
```

---

### **Q: Where does RECENT FORM come from?**
**A: Last 5 matches from historical data**

- **Function**: `get_team_recent_form_original(team_name, data)`
- **File**: `predictor/analytics.py` (lines 693-850)
- **Data**: `football_data1.csv` or `football_data2.csv`
- **Returns**: String like "LWWWW" or "WWDDW"

**For Aston Villa vs Chelsea:**
```python
Aston Villa: "LWWWW" (L=Loss, W=Win) = 12 points
Chelsea: "WWDDW" (W=Win, D=Draw) = 11 points
```

---

### **Q: Where does CONFIDENCE come from?**
**A: Probability of the predicted outcome**

- **Calculation**: `confidence = probabilities[predicted_outcome]`
- **Example**: If predicting "Draw" with 18.2% probability → confidence = 0.182

---

### **Q: Where does HEAD-TO-HEAD HISTORY come from?**
**A: Historical match records from CSV files**

- **Function**: `get_head_to_head_history(home, away, data)`
- **Data**: `football_data1.csv` or `football_data2.csv`
- **Returns**: Last 5 matches with dates, scores, results

---

## 📂 File Locations

| Component | File | Function | Lines |
|-----------|------|----------|-------|
| **Final Prediction** | `predictor/analytics.py` | `advanced_predict_match()` | 1700-2500 |
| **Historical Probabilities** | `predictor/analytics.py` | `calculate_probabilities_original()` | 178-225 |
| **Recent Form** | `predictor/analytics.py` | `get_team_recent_form_original()` | 693-850 |
| **H2H History** | `predictor/analytics.py` | `get_head_to_head_history()` | 228-242 |
| **Team Strength** | `predictor/analytics.py` | `calculate_team_strength()` | 1286-1314 |
| **Django View** | `predictor/views.py` | `predict()` | 275-404 |
| **Result Display** | `predictor/views.py` | `result()` | 1129-1640 |
| **FastAPI Endpoint** | `fastapi_predictor_production.py` | `/predict` | 200-400 |

---

## 🔄 Complete Flow (Simplified)

```
1. User submits → Django views.py
2. Django → FastAPI endpoint
3. FastAPI → advanced_predict_match()
4. Load data → football_data1.csv or football_data2.csv
5. Calculate historical probs → 27.3% / 18.2% / 54.5%
6. Get team form → LWWWW, WWDDW
7. Prepare features → [form, goals, strengths, ...]
8. ML model predicts → "Draw"
9. Return result → Django
10. Save to database → Prediction model
11. Display to user → result.html
```

---

## 💡 Key Functions

### 1. `advanced_predict_match(home_team, away_team, model1, model2)`
**Purpose**: Main prediction function
**Returns**:
```python
{
    'outcome': 'Draw',                    # Final prediction
    'prediction_number': 1,               # 0=Away, 1=Draw, 2=Home
    'probabilities': {                    # Model probabilities
        'Home': 0.273,
        'Draw': 0.182,
        'Away': 0.545
    },
    'confidence': 0.182,                  # Confidence in prediction
    'historical_probs': {                 # Historical data
        'Home Team Win': 27.3,
        'Draw': 18.2,
        'Away Team Win': 54.5
    },
    'model_type': 'Model1',               # Which model used
    'home_form': 'LWWWW',                 # Recent form
    'away_form': 'WWDDW'
}
```

### 2. `calculate_probabilities_original(home, away, data, version)`
**Purpose**: Calculate historical probabilities from H2H data
**Returns**:
```python
{
    'Home Team Win': 27.3,    # Percentage
    'Draw': 18.2,
    'Away Team Win': 54.5
}
```

### 3. `get_team_recent_form_original(team_name, data, version)`
**Purpose**: Get last 5 match results for a team
**Returns**: `"LWWWW"` (string of W/D/L)

### 4. `preprocess_for_models(home_team, away_team, model, data)`
**Purpose**: Prepare features for ML model
**Returns**: Feature array with form, goals, strengths, etc.

---

## 🎯 For Aston Villa vs Chelsea Example

| Component | Value | Source |
|-----------|-------|--------|
| **Final Outcome** | Draw | ML Model prediction |
| **Home Win Prob** | 27.3% | Historical H2H (3/11 matches) |
| **Draw Prob** | 18.2% | Historical H2H (2/11 matches) |
| **Away Win Prob** | 54.5% | Historical H2H (6/11 matches) |
| **Villa Form** | LWWWW | Last 5 matches (12 points) |
| **Chelsea Form** | WWDDW | Last 5 matches (11 points) |
| **Confidence** | 18.2% | Draw probability |
| **Model Type** | Model1 | Premier League uses Model1 |

---

## ❓ FAQ

**Q: Why does model predict "Draw" when Away Win has 54.5% probability?**
A: Model considers recent form (Villa: 12 pts, Chelsea: 11 pts), home advantage, and current team strength. Historical data is just one factor!

**Q: Are probabilities from the model or historical data?**
A: Depends on model type:
- Classification models: Use model probabilities
- Regression models: Use historical probabilities
- Both are adjusted by recent form

**Q: Where is the data stored?**
A: CSV files in `data/` folder:
- `football_data1.csv` - Model1 teams (European leagues)
- `football_data2.csv` - Model2 teams (Other leagues)

**Q: How is confidence calculated?**
A: Confidence = probability of the predicted outcome
- If predicting Draw (18.2%) → confidence = 0.182
- If predicting Away (54.5%) → confidence = 0.545

---

## 🚀 Quick Debug Commands

```bash
# Test prediction for Aston Villa vs Chelsea
python manage.py shell
>>> from predictor.analytics import advanced_predict_match, load_football_data
>>> import joblib
>>> model1 = joblib.load('models/model1.pkl')
>>> result = advanced_predict_match('Aston Villa', 'Chelsea', model1, None)
>>> print(result)

# Check historical data
>>> data = load_football_data(1)
>>> print(data[data['HomeTeam'] == 'Aston Villa'].head())

# Check team form
>>> from predictor.analytics import get_team_recent_form_original
>>> form = get_team_recent_form_original('Aston Villa', data)
>>> print(form)
```

---

## 📝 Summary

**Everything comes from `predictor/analytics.py`:**
- Final prediction → `advanced_predict_match()` using ML model
- Probabilities → Historical H2H data or model output
- Form → Last 5 matches from CSV data
- Confidence → Probability of predicted outcome

**The ML model is the brain, historical data is the reference!** 🧠

