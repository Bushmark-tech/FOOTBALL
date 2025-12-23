"""
FastAPI service for easy model predictions.
Simple REST API to get predictions without complex Django logic.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
import django
import asyncio

# Setup Django (needed for analytics functions)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

import joblib
from predictor.analytics import (
    advanced_predict_match,
    preprocess_for_models,
    load_football_data
)

app = FastAPI(
    title="Football Predictor API",
    description="Simple API for football match predictions",
    version="1.0.0"
)

# Load models at startup
MODEL1 = None
MODEL2 = None

# Cache for football data to avoid loading on every request
FOOTBALL_DATA_CACHE = {
    'data1': None,
    'data2': None,
    'last_loaded': None
}
CACHE_TTL = 3600  # Cache for 1 hour

# Pre-load data at startup to avoid slow loading on first request
def preload_football_data():
    """Pre-load football data at startup to avoid slow first request (non-blocking)."""
    global FOOTBALL_DATA_CACHE
    try:
        from predictor.analytics import load_football_data
        print("[INFO] Pre-loading football data in background...")
        # Load data in background - don't block server startup
        FOOTBALL_DATA_CACHE['data1'] = load_football_data(1, use_cache=True)
        FOOTBALL_DATA_CACHE['data2'] = load_football_data(2, use_cache=True)
        import time
        FOOTBALL_DATA_CACHE['last_loaded'] = time.time()
        print("[OK] Football data pre-loaded successfully")
    except Exception as e:
        print(f"[WARNING] Failed to pre-load football data: {e}")
        print("[INFO] Data will be loaded on first request (may be slightly slower)")

@app.on_event("startup")
async def load_models():
    """Load models when API starts - optimized for fast startup."""
    global MODEL1, MODEL2
    import threading
    
    def load_models_thread():
        """Load models in background thread to avoid blocking."""
        global MODEL1, MODEL2
        try:
            # Use absolute path based on script location
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model1_path = os.path.join(base_dir, 'models', 'model1.pkl')
            model2_path = os.path.join(base_dir, 'models', 'model2.pkl')
            
            print("[INFO] Starting model loading...")
            
            if os.path.exists(model1_path):
                print(f"[INFO] Loading Model 1 from {model1_path}...")
                MODEL1 = joblib.load(model1_path)
                print(f"[OK] Model 1 loaded successfully")
            else:
                print(f"[WARNING] Model 1 not found at {model1_path}")
            
            if os.path.exists(model2_path):
                print(f"[INFO] Loading Model 2 from {model2_path}...")
                MODEL2 = joblib.load(model2_path)
                print(f"[OK] Model 2 loaded successfully")
            else:
                print(f"[WARNING] Model 2 not found at {model2_path}")
                
            print("[OK] Model loading completed")
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to load models: {e}")
            print(traceback.format_exc())
    
    # Load models in background thread so API can start immediately
    thread = threading.Thread(target=load_models_thread, daemon=True)
    thread.start()
    
    # Pre-load football data in background (non-blocking)
    # Data will be loaded on first request if not ready yet
    data_thread = threading.Thread(target=preload_football_data, daemon=True)
    data_thread.start()
    
    # API is ready immediately - models and data load in background
    print("[INFO] Model loading started in background. API is ready.")
    print("[INFO] Data will be loaded in background (first request may be slightly slower if data not ready)")

# Request/Response models
class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    category: Optional[str] = None

class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    prediction: str  # "Home", "Draw", "Away", "1X", "X2", or "12"
    home_score: int
    away_score: int
    probabilities: dict  # {"Home": 0.5, "Draw": 0.3, "Away": 0.2}
    confidence: float
    model_type: str
    form_home: Optional[str] = None
    form_away: Optional[str] = None
    prediction_type: Optional[str] = "Single"  # "Single", "Double Chance", or "Adjusted"
    reasoning: Optional[str] = None  # Explanation of prediction logic

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Football Predictor API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Get match prediction",
            "/health": "GET - Check API health",
            "/models": "GET - Check model status"
        }
    }

@app.get("/health")
async def health():
    """Check API health."""
    return {
        "status": "healthy",
        "api_ready": True,
        "model1_loaded": MODEL1 is not None,
        "model2_loaded": MODEL2 is not None,
        "message": "API is running. Models may still be loading."
    }

@app.get("/models")
async def models_status():
    """Check model status."""
    status = {
        "model1": {
            "loaded": MODEL1 is not None,
            "type": type(MODEL1).__name__ if MODEL1 else None,
            "features": MODEL1.n_features_in_ if MODEL1 and hasattr(MODEL1, 'n_features_in_') else None
        },
        "model2": {
            "loaded": MODEL2 is not None,
            "type": type(MODEL2).__name__ if MODEL2 else None,
            "features": MODEL2.n_features_in_ if MODEL2 and hasattr(MODEL2, 'n_features_in_') else None
        }
    }
    return status

def smart_prediction_logic(model_prediction: str, prob_home: float, prob_draw: float, prob_away: float) -> tuple:
    """
    Smart prediction logic that combines model prediction with historical probabilities.
    
    Returns: (final_prediction, prediction_type, confidence, reasoning)
    
    Prediction types:
    - "Single": Regular prediction (Home, Draw, Away)
    - "Double Chance": 1X (Home or Draw), X2 (Draw or Away), 12 (Home or Away)
    - "Adjusted": Model prediction adjusted based on historical data
    """
    
    # Find highest historical probability
    probs = {"Home": prob_home, "Draw": prob_draw, "Away": prob_away}
    max_prob_outcome = max(probs, key=probs.get)
    max_prob = probs[max_prob_outcome]
    
    # Sort probabilities to find second highest
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    second_highest = sorted_probs[1]
    
    print(f"\n[SMART LOGIC] Model: {model_prediction}, Historical: Home={prob_home*100:.1f}%, Draw={prob_draw*100:.1f}%, Away={prob_away*100:.1f}%")
    print(f"[SMART LOGIC] Highest historical: {max_prob_outcome} ({max_prob*100:.1f}%)")
    
    # Rule 1: Model and History Agree (High Confidence)
    if model_prediction == max_prob_outcome and max_prob > 0.40:
        confidence = max_prob
        reasoning = f"Model and historical data agree: {model_prediction} is most likely ({max_prob*100:.1f}%)"
        print(f"[SMART LOGIC] Rule 1: Agreement - Using {model_prediction} with high confidence")
        return model_prediction, "Single", confidence, reasoning
    
    # Rule 2: Draw Dominance (Double Chance)
    if prob_draw > 0.50 and model_prediction != "Draw":
        # Draw is very likely, but model says Home/Away
        if model_prediction == "Home":
            final_pred = "1X"  # Home or Draw
            reasoning = f"Draw probability is high ({prob_draw*100:.1f}%), suggesting Home or Draw"
        else:  # Away
            final_pred = "X2"  # Draw or Away
            reasoning = f"Draw probability is high ({prob_draw*100:.1f}%), suggesting Draw or Away"
        
        confidence = (prob_draw + probs[model_prediction]) / 2
        print(f"[SMART LOGIC] Rule 2: Draw dominance - Using {final_pred} (Double Chance)")
        return final_pred, "Double Chance", confidence, reasoning
    
    # Rule 3: Model and History Disagree with Uncertainty (Double Chance)
    if model_prediction != max_prob_outcome and max_prob < 0.45:
        # No clear winner, use double chance for top 2
        top_two = [sorted_probs[0][0], sorted_probs[1][0]]
        
        if "Home" in top_two and "Draw" in top_two:
            final_pred = "1X"
            reasoning = f"Uncertainty between Home ({prob_home*100:.1f}%) and Draw ({prob_draw*100:.1f}%)"
        elif "Draw" in top_two and "Away" in top_two:
            final_pred = "X2"
            reasoning = f"Uncertainty between Draw ({prob_draw*100:.1f}%) and Away ({prob_away*100:.1f}%)"
        else:  # Home and Away
            final_pred = "12"
            reasoning = f"Uncertainty between Home ({prob_home*100:.1f}%) and Away ({prob_away*100:.1f}%), Draw unlikely"
        
        confidence = (sorted_probs[0][1] + sorted_probs[1][1]) / 2
        print(f"[SMART LOGIC] Rule 3: Disagreement with uncertainty - Using {final_pred} (Double Chance)")
        return final_pred, "Double Chance", confidence, reasoning
    
    # Rule 4: Clear Historical Winner, Model Disagrees
    if max_prob > 0.50 and model_prediction != max_prob_outcome:
        confidence = max_prob * 0.8  # Reduce confidence due to disagreement
        reasoning = f"Historical data strongly suggests {max_prob_outcome} ({max_prob*100:.1f}%), overriding model's {model_prediction}"
        print(f"[SMART LOGIC] Rule 4: Clear historical winner - Using {max_prob_outcome} (Adjusted)")
        return max_prob_outcome, "Adjusted", confidence, reasoning
    
    # Rule 5: Very Close Probabilities (Use Model with Low Confidence)
    prob_range = max_prob - sorted_probs[2][1]
    if prob_range < 0.10:
        confidence = max_prob * 0.7  # Low confidence
        reasoning = f"Very close probabilities (range: {prob_range*100:.1f}%), using model prediction with caution"
        print(f"[SMART LOGIC] Rule 5: Very close probabilities - Using {model_prediction} (Low confidence)")
        return model_prediction, "Single", confidence, reasoning
    
    # Default: Use model prediction with medium confidence
    confidence = max(prob_home, prob_draw, prob_away) * 0.85
    reasoning = f"Using model prediction with medium confidence"
    print(f"[SMART LOGIC] Default: Using {model_prediction} (Medium confidence)")
    return model_prediction, "Single", confidence, reasoning

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Get match prediction.
    
    Example request:
    {
        "home_team": "Lugano",
        "away_team": "Luzern",
        "category": "Others"
    }
    """
    try:
        # Wait for models to load if they're still loading (with shorter timeout)
        import time
        max_wait = 5  # Wait up to 5 seconds for models to load (reduced from 60)
        wait_time = 0
        while (MODEL1 is None and MODEL2 is None) and wait_time < max_wait:
            await asyncio.sleep(0.1)
            wait_time += 0.1
        
        if MODEL1 is None and MODEL2 is None:
            raise HTTPException(
                status_code=503,
                detail="Models are still loading. Please try again in a moment."
            )
        
        # Wait for data to be pre-loaded (with shorter timeout for faster response)
        # If data isn't ready, load it on-demand (slightly slower but server starts faster)
        max_data_wait = 2  # Reduced from 30 to 2 seconds - load on-demand if not ready
        data_wait_time = 0
        while (FOOTBALL_DATA_CACHE['data1'] is None and FOOTBALL_DATA_CACHE['data2'] is None) and data_wait_time < max_data_wait:
            await asyncio.sleep(0.1)
            data_wait_time += 0.1
        
        # Use advanced prediction logic with pre-loaded data cache
        # Patch load_football_data to use our in-memory cache for speed
        from predictor import analytics
        original_load = analytics.load_football_data
        
        def fast_load_football_data(dataset=1, use_cache=True):
            """Fast cached version that uses pre-loaded data or loads on-demand."""
            global FOOTBALL_DATA_CACHE
            data_key = f'data{dataset}'
            
            # Return pre-loaded data if available (much faster than loading from file)
            if FOOTBALL_DATA_CACHE[data_key] is not None:
                return FOOTBALL_DATA_CACHE[data_key]
            
            # If not pre-loaded, load and cache it on-demand (lazy loading)
            print(f"[INFO] Loading football data {dataset} on-demand (not pre-loaded yet)...")
            data = original_load(dataset, use_cache=True)
            FOOTBALL_DATA_CACHE[data_key] = data
            FOOTBALL_DATA_CACHE['last_loaded'] = time.time()
            print(f"[OK] Football data {dataset} loaded and cached")
            return data
        
        # Temporarily replace function for this request
        analytics.load_football_data = fast_load_football_data
        try:
            # Add timing to debug performance
            start_time = time.time()
            print("\n" + "="*70)
            print(f"[DEBUG] Starting prediction for {request.home_team} vs {request.away_team}")
            print("="*70)
            
            result = advanced_predict_match(
                request.home_team,
                request.away_team,
                MODEL1,
                MODEL2
            )
            
            elapsed = time.time() - start_time
            print(f"[DEBUG] ✅ Prediction completed in {elapsed:.2f} seconds")
            print("="*70 + "\n")
        finally:
            # Restore original
            analytics.load_football_data = original_load
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"Prediction failed - check team names: {request.home_team} vs {request.away_team}"
            )
        
        # Skip form data loading to speed up prediction (it's optional and can be slow)
        # Form data can be calculated on the result page if needed
        form_home = None
        form_away = None
        
        # Extract probabilities
        # CRITICAL FIX: Use historical_probs (string keys) instead of probabilities (integer keys)
        # historical_probs has keys: "Home Team Win", "Draw", "Away Team Win" in percentage format (0-100)
        # probabilities has keys: 0=Away, 1=Draw, 2=Home in decimal format (0-1)
        
        # Try historical_probs first (more reliable), fallback to integer-keyed probabilities
        historical_probs = result.get('historical_probs', {})
        if historical_probs and isinstance(historical_probs, dict) and len(historical_probs) > 0:
            # Historical probabilities are in percentage format (0-100), convert to decimal (0-1)
            prob_dict = {
                "Home": float(historical_probs.get("Home Team Win", 33.0)) / 100.0,
                "Draw": float(historical_probs.get("Draw", 33.0)) / 100.0,
                "Away": float(historical_probs.get("Away Team Win", 33.0)) / 100.0
            }
            print(f"[DEBUG] Using historical_probs (percentage format): {historical_probs}")
            print(f"[DEBUG] Converted to prob_dict (decimal format): {prob_dict}")
        else:
            # Fallback to integer-keyed probabilities if historical_probs not available
            probs = result.get('probabilities', {})
            prob_dict = {
                "Home": float(probs.get(2, probs.get("Home", 0.33))),  # 2 = Home
                "Draw": float(probs.get(1, probs.get("Draw", 0.33))),  # 1 = Draw
                "Away": float(probs.get(0, probs.get("Away", 0.33)))   # 0 = Away
            }
            print(f"[DEBUG] Using integer-keyed probabilities (decimal format): {probs}")
            print(f"[DEBUG] Converted to prob_dict (decimal format): {prob_dict}")
        
        # Normalize probabilities to ensure they sum to exactly 1.0
        total = sum(prob_dict.values())
        if total > 0 and abs(total - 1.0) > 0.01:  # Only normalize if not already normalized
            prob_dict = {k: v/total for k, v in prob_dict.items()}
            print(f"[DEBUG] Probabilities normalized (sum was {total:.4f})")
        
        # Ensure probabilities are valid (0-1 range)
        for key in prob_dict:
            prob_dict[key] = max(0.0, min(1.0, prob_dict[key]))
        
        print(f"[DEBUG] Final normalized prob_dict (decimal, sum={sum(prob_dict.values()):.4f}): {prob_dict}")
        print(f"[DEBUG] Final probabilities as percentages: Home={prob_dict['Home']*100:.1f}%, Draw={prob_dict['Draw']*100:.1f}%, Away={prob_dict['Away']*100:.1f}%")
        
        # Get model's original prediction
        model_outcome = result.get('outcome', 'Draw')
        
        # Apply smart prediction logic
        final_prediction, prediction_type, smart_confidence, reasoning = smart_prediction_logic(
            model_outcome,
            prob_dict['Home'],
            prob_dict['Draw'],
            prob_dict['Away']
        )
        
        print(f"[SMART LOGIC] Final prediction: {final_prediction} (Type: {prediction_type}, Confidence: {smart_confidence*100:.1f}%)")
        print(f"[SMART LOGIC] Reasoning: {reasoning}")
        
        # Determine scores based on final prediction
        if final_prediction in ["Home", "1X", "12"]:
            home_score = 2
            away_score = 1
        elif final_prediction in ["Away", "X2"]:
            home_score = 1
            away_score = 2
        else:  # Draw
            home_score = 1
            away_score = 1
        
        # Get timing info from result if available (for debugging)
        timing_info = result.get('debug_timings', {})
        
        response = PredictionResponse(
            home_team=request.home_team,
            away_team=request.away_team,
            prediction=final_prediction,
            home_score=home_score,
            away_score=away_score,
            probabilities=prob_dict,
            confidence=float(smart_confidence),
            model_type=result.get('model_type', 'Unknown'),
            form_home=form_home if form_home else None,
            form_away=form_away if form_away else None,
            prediction_type=prediction_type,
            reasoning=reasoning
        )
        
        # Print timing to console (always visible)
        if timing_info:
            print("\n" + "="*70)
            print(f"[PERF] Timing for {request.home_team} vs {request.away_team}:")
            for key, value in sorted(timing_info.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True):
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.2f}s")
            print("="*70 + "\n")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Prediction failed: {e}")
        print(error_details)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}. Check server logs for details."
        )

@app.get("/predict/simple")
async def predict_simple(home_team: str, away_team: str):
    """
    Simple GET endpoint for quick predictions.
    
    Example: /predict/simple?home_team=Lugano&away_team=Luzern
    """
    request = PredictionRequest(home_team=home_team, away_team=away_team)
    return await predict(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

