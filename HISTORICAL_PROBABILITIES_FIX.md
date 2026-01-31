# Historical Probabilities Fix - Summary

## Problem Identified

The "Historical Probabilities" section on the results page was showing **incorrect data** that didn't match actual head-to-head match history between teams.

### Example Issue:
For **Leeds vs Arsenal**, the system showed:
- Leeds Win: 35%
- Draw: 35%  
- Arsenal Win: 30%

But the prediction was "LEEDS OR DRAW" which didn't align with these probabilities.

## Root Cause

The code in `predictor/views.py` (lines 2294-2320) was using `calculate_probabilities_original()` to generate "historical" probabilities. However, this function **does NOT analyze actual historical match data**.

Instead, `calculate_probabilities_original()` calculates probabilities based on:
- **Team strength differences** (calculated from recent form and goals)
- **Predefined probability curves** based on strength gaps
- **NO actual head-to-head match analysis**

This is why the probabilities appeared generic and didn't reflect true historical matchups.

## Solution Implemented

### Changed the calculation method:

**BEFORE (Incorrect):**
```python
hist_raw = calculate_probabilities_original(home_team, away_team, calc_data)
```

**AFTER (Correct):**
```python
# Try to calculate TRUE H2H probabilities from actual match history
hist_raw = calculate_probabilities_model2(home_team, away_team, calc_data, version=version)

# If no H2H data exists, fall back to team strength estimates
if not hist_raw:
    logger.info(f"[RESULT VIEW] No H2H data found, trying team strength estimates")
    hist_raw = calculate_probabilities_original(home_team, away_team, calc_data, version=version)
```

### What `calculate_probabilities_model2()` does:

1. **Finds actual head-to-head matches** between the two teams in the historical database
2. **Analyzes match outcomes** (Home wins, Draws, Away wins)
3. **Applies weighted scoring**:
   - Direct matches (Team A home vs Team B away): Weight 1.0
   - Reverse matches (Team B home vs Team A away): Weight 0.6 (accounts for home advantage)
4. **Uses Laplace smoothing** to handle small sample sizes
5. **Returns TRUE historical probabilities** based on actual past results

### Additional Improvements:

1. **Dataset Selection**: The fix now properly selects the correct dataset (1 or 2) based on team categories
2. **Fallback Logic**: If no H2H data exists, it gracefully falls back to team strength estimates
3. **Better Logging**: Clear log messages indicate whether true H2H data or estimates are being used

## Expected Results

After this fix:

✅ **Historical Probabilities** will show actual statistics from past matches between the teams
✅ **Data accuracy** improves significantly for teams with match history
✅ **Transparency** - Users can see if data is based on actual history or estimates
✅ **Consistency** - Predictions and historical data will align better

## Testing

To test the fix:
1. Make a new prediction for **Leeds vs Arsenal**
2. Check the "Historical Probabilities" section
3. Verify the percentages reflect actual head-to-head match outcomes
4. If teams have no H2H history, the system will show a warning message

## Files Modified

- `d:\React\FOOTBALL\predictor\views.py` (lines 2294-2347)
  - Replaced `calculate_probabilities_original` with `calculate_probabilities_model2`
  - Added proper dataset selection logic
  - Improved fallback handling

## Impact

- **Severity**: High - This was showing incorrect data to users
- **Complexity**: 7/10 - Required understanding of the prediction pipeline
- **User Benefit**: Significantly improves trust and accuracy of displayed statistics
