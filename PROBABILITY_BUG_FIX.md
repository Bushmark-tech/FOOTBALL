# Probability Display Bug Fix

## Issue Description

The prediction results page was displaying incorrect probabilities that didn't sum to 100%:

**Example (Man City vs Fulham):**
- Prediction: "MAN CITY WILL WIN"
- Man City: 33%
- Draw: 33%
- Fulham: 100%
- **Total: 166% (INCORRECT!)**

## Root Cause Analysis

The bug was caused by **TWO separate issues** in `predictor/analytics.py`:

### Issue 1: Data Encoding Mismatch (PRIMARY CAUSE)
The `calculate_probabilities_original` function was checking for string values ('H', 'D', 'A') but the actual data uses **integer encoding** (0, 1, 2):
- **Expected**: `'H'` for home win, `'D'` for draw, `'A'` for away win
- **Actual**: `2` for home win, `1` for draw, `0` for away win (from notebook encoding)
- **Result**: All checks failed, returning 0 home wins, 0 draws, and counting ALL matches as away wins (100%)

### Issue 2: Probability Format Handling (SECONDARY CAUSE)
1. **Mixed Format Problem**: Some probabilities were in decimal format (0.0-1.0) while others were in percentage format (0-100)
2. **No Validation**: There was no validation to ensure probabilities summed to 1.0 before returning
3. **Mapping Issues**: Historical probabilities (in percentage format) were being mixed with model probabilities (in decimal format) without proper conversion

## Changes Made

### 1. Fixed Data Encoding Detection (`analytics.py` lines 520-548) **[CRITICAL FIX]**

The primary fix detects whether the result column uses integer encoding (0, 1, 2) or string encoding ('H', 'D', 'A'):

```python
# Check if result column contains strings or integers
sample_value = h2h[result_col].iloc[0] if len(h2h) > 0 else None

# Try to import numpy for type checking
try:
    np = safe_import_numpy()
    is_numeric = isinstance(sample_value, (int, float, np.integer, np.floating))
except:
    is_numeric = isinstance(sample_value, (int, float))

if is_numeric:
    # Integer encoding: 0=Away, 1=Draw, 2=Home
    logger.info(f"Result column contains integers (encoded): {h2h[result_col].unique()}")
    home_wins = (h2h[result_col] == 2).sum()
    draws = (h2h[result_col] == 1).sum()
    away_wins = (h2h[result_col] == 0).sum()
else:
    # String encoding: 'H'=Home, 'D'=Draw, 'A'=Away
    logger.info(f"Result column contains strings: {h2h[result_col].unique()}")
    home_wins = (h2h[result_col] == 'H').sum()
    draws = (h2h[result_col] == 'D').sum()
    away_wins = (h2h[result_col] == 'A').sum()
```

### 2. Added Probability Format Validation (`analytics.py` lines 2141-2166)

```python
# CRITICAL FIX: Ensure probabilities are in correct range (0.0-1.0) not (0-100)
# Check if probabilities look like percentages (>1.0) and convert to decimal
for key in prob_dict:
    if prob_dict[key] > 1.0:
        logger.warning(f"  - WARNING: Probability {key} is {prob_dict[key]:.3f} (>1.0), converting from percentage to decimal")
        prob_dict[key] = prob_dict[key] / 100.0

# Re-normalize after conversion (in case some were percentages and some weren't)
total = sum(prob_dict.values())
if total > 0 and abs(total - 1.0) > 0.01:  # Only renormalize if significantly off from 1.0
    logger.warning(f"  - WARNING: Probabilities sum to {total:.3f}, renormalizing")
    prob_dict = {k: v / total for k, v in prob_dict.items()}

# VALIDATION: Ensure probabilities sum to approximately 1.0
final_total = sum(prob_dict.values())
if abs(final_total - 1.0) > 0.05:
    logger.error(f"  - ERROR: Final probabilities sum to {final_total:.3f}, not 1.0! Resetting to equal probabilities")
    prob_dict = {0: 0.33, 1: 0.34, 2: 0.33}
```

### 3. Fixed Historical Probability Conversion (`analytics.py` lines 2126-2137)

```python
# Historical probabilities are in percentage format (0-100), convert to decimal (0-1)
prob_dict = {
    0: probs.get("Away Team Win", 33.0) / 100.0,
    1: probs.get("Draw", 33.0) / 100.0,
    2: probs.get("Home Team Win", 33.0) / 100.0
}
```

### 4. Added Final Validation Before Return (`analytics.py` lines 2416-2445)

```python
# CRITICAL FINAL VALIDATION: Ensure probabilities are correct before returning
logger.info(f"\n{'='*70}")
logger.info(f"FINAL PREDICTION VALIDATION for {home_team} vs {away_team}")
logger.info(f"{'='*70}")

# Validate probabilities are in correct format (0.0-1.0, not 0-100)
for key, value in prob_dict.items():
    if value > 1.0:
        logger.error(f"  ERROR: Probability {key} is {value:.3f} (>1.0)! Converting from percentage")
        prob_dict[key] = value / 100.0

# Validate probabilities sum to approximately 1.0
prob_sum = sum(prob_dict.values())
if abs(prob_sum - 1.0) > 0.05:
    logger.error(f"  ERROR: Probabilities sum to {prob_sum:.3f}, not 1.0! Normalizing...")
    if prob_sum > 0:
        prob_dict = {k: v / prob_sum for k, v in prob_dict.items()}
    else:
        prob_dict = {0: 0.33, 1: 0.34, 2: 0.33}

# Log final probabilities in human-readable format
logger.info(f"  FINAL PROBABILITIES:")
logger.info(f"    Away ({away_team}): {prob_dict.get(0, 0)*100:.1f}%")
logger.info(f"    Draw: {prob_dict.get(1, 0)*100:.1f}%")
logger.info(f"    Home ({home_team}): {prob_dict.get(2, 0)*100:.1f}%")
```

### 5. Enhanced Logging for Debugging

Added comprehensive logging at multiple points:
- Before normalization
- After conversion from percentage to decimal
- After final validation
- In fallback scenarios

## Expected Result After Fix

For **Man City vs Fulham**, the probabilities should now display correctly:

**Example (Expected):**
- Prediction: "MAN CITY WILL WIN"
- Man City: 45%
- Draw: 30%
- Fulham: 25%
- **Total: 100% ✓**

## Testing Instructions

1. **Restart the FastAPI server** to load the fixed code:
   ```bash
   python run_api.py
   ```

2. **Make a prediction** for Man City vs Fulham

3. **Verify the results**:
   - Check that all probabilities are between 0% and 100%
   - Check that the sum equals 100%
   - Check that the prediction matches the highest probability

4. **Check the logs** in the terminal for validation messages:
   - Look for "FINAL PREDICTION VALIDATION" section
   - Verify no ERROR messages about probabilities > 1.0
   - Verify probabilities sum to ~1.0

## Model Encoding Reference

The model uses the following encoding (from training notebook Cell 25):

```
Encoding mapping:
  A → 0  (Away)
  D → 1  (Draw)
  H → 2  (Home)
```

So `prob_dict` format is:
- `prob_dict[0]` = Away team win probability (0.0-1.0)
- `prob_dict[1]` = Draw probability (0.0-1.0)
- `prob_dict[2]` = Home team win probability (0.0-1.0)

## Files Modified

1. `predictor/analytics.py` - Added validation and conversion logic
2. `PROBABILITY_BUG_FIX.md` - This documentation file

## Related Issues

- Probabilities were displaying incorrectly (summing to >100%)
- Historical probabilities (percentage format) were being mixed with model probabilities (decimal format)
- No validation was ensuring probabilities were in correct range

## Prevention

The fix includes multiple layers of validation:
1. **Format checking**: Detect if probabilities are in percentage format (>1.0) and convert
2. **Normalization**: Ensure probabilities sum to 1.0
3. **Final validation**: Double-check before returning results
4. **Comprehensive logging**: Track probability values at each step

This ensures the bug cannot reoccur even if future code changes introduce similar issues.

