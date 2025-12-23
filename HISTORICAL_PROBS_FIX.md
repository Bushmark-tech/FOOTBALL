# Historical Probabilities Display Fix

## Issue
The "Past Performance" section was showing the same probabilities as the "Win Probability" section, instead of showing the actual historical probabilities from past matches.

## Root Cause
The template was using `{{ probabilities.Home }}`, `{{ probabilities.Draw }}`, `{{ probabilities.Away }}` for both sections, but these are the **model probabilities** (from the smart logic prediction), not the **historical probabilities** (from past H2H matches).

## Solution

### 1. Backend Changes (`predictor/views.py`)

Added a separate `historical_probabilities` variable to store the raw historical probabilities:

```python
# Line 1316-1334
historical_probs_raw = calculate_probabilities_original(home_team, away_team, data, version="v1")
if historical_probs_raw:
    # Convert to decimal and normalize
    probabilities = {
        'Home': historical_probs_raw.get("Home Team Win", 33.0) / 100.0,
        'Draw': historical_probs_raw.get("Draw", 33.0) / 100.0,
        'Away': historical_probs_raw.get("Away Team Win", 33.0) / 100.0
    }
    # Normalize
    total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
    if total_prob > 0:
        probabilities['Home'] = probabilities['Home'] / total_prob
        probabilities['Draw'] = probabilities['Draw'] / total_prob
        probabilities['Away'] = probabilities['Away'] / total_prob
    # Store separately for Past Performance section
    historical_probabilities = probabilities.copy()
```

Added to context (line 1803):

```python
context = {
    ...
    'probabilities': probabilities,  # Model probabilities (after smart logic)
    'historical_probabilities': historical_probabilities,  # Raw historical probabilities
    ...
}
```

### 2. Frontend Changes (`templates/predictor/result.html`)

Updated the "Past Performance" section to use `historical_probabilities`:

```html
<!-- Before -->
<div class="stat-value" data-prob="{{ probabilities.Home }}">0%</div>

<!-- After -->
<div class="stat-value" data-prob="{{ historical_probabilities.Home }}">0%</div>
```

Changed class names to avoid conflicts:
- `.prob-home` → `.prob-home-hist`
- `.prob-draw` → `.prob-draw-hist`
- `.prob-away` → `.prob-away-hist`

## Result

Now the page correctly shows:

### Win Probability (Top Section)
Shows the **model's final prediction** after applying smart logic:
- Example: Man City 60%, Draw 20%, Fulham 20%
- These are the probabilities from the prediction model with smart logic applied

### Past Performance (Historical Section)
Shows the **actual historical probabilities** from past H2H matches:
- Example: Home Win 72.7%, Draw 9.1%, Away Win 18.2%
- These are calculated directly from past match results

## Files Modified
1. `predictor/views.py` - Added `historical_probabilities` variable and context
2. `templates/predictor/result.html` - Updated to use `historical_probabilities` for Past Performance section

## Testing
Test by making a prediction for teams with H2H history (e.g., Man City vs Liverpool) and verify:
1. ✅ Win Probability shows model predictions (with smart logic)
2. ✅ Past Performance shows historical probabilities
3. ✅ Both sections display correctly and sum to 100%
4. ✅ Animations work for both sections

## Status
✅ **FIXED** - Historical probabilities now display correctly in the Past Performance section.

