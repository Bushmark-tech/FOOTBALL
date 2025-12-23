# How to Debug Performance Issues

## Step 1: View FastAPI Console Output

The FastAPI server prints all debug information to the console where you ran `python run_api.py`.

### To see the debug output:

1. **Find the FastAPI terminal/console** where you see messages like:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8001
   [INFO] Starting model loading...
   ```

2. **Make a prediction** (through the web interface or test script)

3. **Watch the console** - you'll see output like:
   ```
   ======================================================================
   [DEBUG] Starting prediction for Team1 vs Team2
   ======================================================================
   
   [PERF] ⏱️  PERFORMANCE TIMING BREAKDOWN:
   ----------------------------------------------------------------------
     calculate_probabilities         :  15.30s (80.5%)
     load_data_1                     :   2.50s (13.2%)
     compute_features                :   1.20s (6.3%)
     TOTAL                           :  19.00s (100.0%)
   
   [DEBUG] ✅ Prediction completed in 19.02 seconds
   ======================================================================
   ```

## Step 2: Use the Test Script

Run the test script to test the API directly:

```bash
cd "C:\Users\user\Desktop\Football djang\Football-main"
python test_api_performance.py
```

This will:
- Test multiple predictions
- Show timing for each request
- Help identify which operations are slow

## Step 3: Identify the Bottleneck

Look at the `[PERF]` output. The operation with the **highest time** is your bottleneck:

- **`calculate_probabilities`** - Slow pandas operations on large dataframes
- **`load_data_1` or `load_data_2`** - Loading CSV files (should be cached)
- **`compute_features`** - Feature computation from data
- **`total`** - Total prediction time

## Step 4: What to Do Next

1. **Share the timing output** - Copy the `[PERF]` output from the console
2. **Note which operation is slowest** - This tells us what to optimize
3. **Check if it's consistent** - Run 2-3 predictions to see if timings are consistent

## Common Issues:

### Issue: `load_data` is slow (even with caching)
- **Cause**: Data files are very large or cache isn't working
- **Solution**: Check if pre-loading is working (you should see `[OK] Football data pre-loaded successfully`)

### Issue: `calculate_probabilities` is very slow (15+ seconds)
- **Cause**: Large pandas operations filtering/searching through huge dataframes
- **Solution**: Need to optimize the pandas filtering operations

### Issue: First prediction slow, subsequent ones fast
- **Cause**: Data is loading on first request (pre-load might not be ready)
- **Solution**: Wait 10-20 seconds after starting FastAPI before testing

## Quick Test Command:

```bash
# Test a single prediction via command line
curl -X POST "http://127.0.0.1:8001/predict" -H "Content-Type: application/json" -d "{\"home_team\":\"Lugano\",\"away_team\":\"Luzern\",\"category\":\"Others\"}"
```

Or use the test script:
```bash
python test_api_performance.py
```

