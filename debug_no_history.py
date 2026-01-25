
import os
import sys
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models, process_prediction_probabilities

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_no_history():
    print("DEBUGGING NO HISTORY (Ghost FC vs Spirit United)")
    print("="*50)
    
    # 1. Load Models (Mock or Real)
    # We can pass None to force fallback logic inside analytics if we want, 
    # but analytics.py normally tries to use them.
    # Let's try to load them to be authentic.
    try:
        model1, model2 = load_prediction_models()
    except:
        model1, model2 = None, None

    # 2. Call advanced_predict_match with fake teams
    home_team = "Ghost FC"
    away_team = "Spirit United"
    
    print(f"\nCalling advanced_predict_match('{home_team}', '{away_team}')...")
    result = advanced_predict_match(home_team, away_team, model1, model2)
    
    if result:
        print("\n--- Advanced Result Metadata ---")
        if 'historical_probs' in result:
            print(f"historical_probs: {result['historical_probs']}")
        else:
            print("historical_probs: NOT FOUND (As expected)")
            
        print(f"Model Type: {result.get('model_type')}")
        
        # 3. Process Probabilities
        probs, outcome = process_prediction_probabilities(result)
        print(f"Final Processed Probs: {probs}")
        print(f"Final Outcome: {outcome}")
        
        # We expect fallback probabilities because no history and likely no model features
        # Fallback in analytics.py (BlendedCalculator) is {0: 0.33, 1: 0.34, 2: 0.33}
        
    else:
        print("advanced_predict_match returned None")

if __name__ == "__main__":
    debug_no_history()
