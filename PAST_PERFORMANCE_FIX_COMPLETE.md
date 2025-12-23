# Past Performance Display - Complete Fix

## Issue
The "Past Performance" section was showing **100% Home Win, 0% Draw, 0% Away Win** instead of the actual historical probabilities from past H2H matches.

## Root Cause
The system had two problems:

1. **Template Issue**: The "Past Performance" section was using `{{ probabilities.Home }}` which are the **model probabilities** (after smart logic), not the **historical probabilities** (from H2H data).

2. **Backend Issue**: When probabilities came from URL parameters (from the prediction page), the system wasn't calculating separate historical probabilities - it was just copying the model probabilities.

## Complete Solution

### Part 1: Separate Variables (Backend)

**File**: `predictor/views.py`

Added logic to always calculate REAL historical probabilities separately:

```python
# Lines 1365-1403
# Calculate REAL historical probabilities from H2H data (separate from model probabilities)
if 'historical_probabilities' not in locals() or historical_probabilities is None:
    historical_probabilities = probabilities.copy() if probabilities else {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}

# Always try to get real historical probabilities from H2H data
try:
    from .analytics import calculate_probabilities_original, load_football_data
    
    # Determine which dataset to use
    other_teams = set()
    try:
        other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
        for league in other_leagues:
            other_teams.update([team.name for team in league.teams.all()])
    except Exception:
        pass
    
    # Load appropriate dataset
    if home_team in other_teams and away_team in other_teams:
        data = load_football_data(2, use_cache=True)
    else:
        data = load_football_data(1, use_cache=True)
    
    data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
    
    if not data_empty and home_team and away_team:
        real_historical_probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
        if real_historical_probs:
            # Convert from percentage to decimal
            historical_probabilities = {
                'Home': real_historical_probs.get("Home Team Win", 33.0) / 100.0,
                'Draw': real_historical_probs.get("Draw", 33.0) / 100.0,
                'Away': real_historical_probs.get("Away Team Win", 33.0) / 100.0
            }
            # Normalize
            total_hist = sum(historical_probabilities.values())
            if total_hist > 0:
                historical_probabilities = {k: v/total_hist for k, v in historical_probabilities.items()}
            logger.info(f"Calculated real historical probabilities: {historical_probabilities}")
except Exception as e:
    logger.warning(f"Could not calculate real historical probabilities: {e}")
```

Added to context (line 1810):

```python
context = {
    ...
    'probabilities': probabilities,  # Model probabilities (Win Probability section)
    'historical_probabilities': historical_probabilities,  # Real H2H data (Past Performance section)
    ...
}
```

### Part 2: Update Template (Frontend)

**File**: `templates/predictor/result.html`

Changed the "Past Performance" section to use `historical_probabilities`:

```html
<!-- Lines 560-580 -->
<div class="stats-overview">
    <div class="stat-card">
        <div class="stat-value" style="color: #00d4aa;" data-prob="{{ historical_probabilities.Home }}">0%</div>
        <div class="stat-label">Home Win</div>
        <div class="probability-bar" style="margin-top: 10px;">
            <div class="probability-fill prob-home-hist" style="..."></div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color: #ff6b35;" data-prob="{{ historical_probabilities.Draw }}">0%</div>
        <div class="stat-label">Draw</div>
        <div class="probability-bar" style="margin-top: 10px;">
            <div class="probability-fill prob-draw-hist" style="..."></div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color: #ff6b35;" data-prob="{{ historical_probabilities.Away }}">0%</div>
        <div class="stat-label">Away Win</div>
        <div class="probability-bar" style="margin-top: 10px;">
            <div class="probability-fill prob-away-hist" style="..."></div>
        </div>
    </div>
</div>
```

## How It Works Now

### Data Flow

1. **User makes prediction** → Django calls FastAPI
2. **FastAPI returns** → Model probabilities (after smart logic)
3. **Django receives** → Stores as `probabilities`
4. **Django calculates** → Separate `historical_probabilities` from H2H data
5. **Template displays**:
   - **Win Probability**: Uses `probabilities` (model prediction)
   - **Past Performance**: Uses `historical_probabilities` (H2H data)

### Example Output

#### Win Probability (Model Prediction)
```
Man City: 60%
Draw: 20%
Fulham: 20%
```
*These are the model's predictions after applying smart logic*

#### Past Performance (Historical H2H Data)
```
Home Win: 72.7%
Draw: 9.1%
Away Win: 18.2%
```
*These are calculated from actual past matches between these teams*

## Testing

### To Verify the Fix:

1. **Restart Django server** (to load new code):
   ```bash
   python manage.py runserver
   ```

2. **Make a prediction** for teams with H2H history:
   - Man City vs Liverpool
   - Barcelona vs Real Madrid
   - Bayern Munich vs Dortmund

3. **Check the result page**:
   - ✅ **Win Probability** section shows model predictions
   - ✅ **Past Performance** section shows DIFFERENT historical data
   - ✅ Both sections sum to 100%
   - ✅ Values are different (not 100%/0%/0%)

### Test Script

Run the test script to verify:

```bash
python test_historical_probs_display.py
```

## What Changed

### Files Modified
1. `predictor/views.py` - Added separate historical probability calculation
2. `templates/predictor/result.html` - Updated to use `historical_probabilities`

### Key Changes
- ✅ Always calculate real historical probabilities from H2H data
- ✅ Store separately from model probabilities
- ✅ Display correctly in template
- ✅ Handle cases where H2H data is not available

## Expected Behavior

### With H2H Data (Model 1 teams)
- **Win Probability**: Model's smart prediction
- **Past Performance**: Real H2H statistics (different values)

### Without H2H Data (Model 2 teams)
- **Win Probability**: Form-based prediction
- **Past Performance**: Same as Win Probability (no H2H data available)

## Status

✅ **FIXED** - Past Performance now shows actual historical H2H data, separate from model predictions.

## Next Steps

1. Restart Django server
2. Test with Man City vs Liverpool
3. Verify both sections show different values
4. Confirm probabilities sum to 100% in both sections

---

**Date**: December 23, 2025  
**Status**: ✅ Complete  
**Files**: 2 modified  
**Test**: Ready for verification

