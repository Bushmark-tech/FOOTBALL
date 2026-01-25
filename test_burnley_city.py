import os
import sys
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models, process_prediction_probabilities

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_burnley_city():
    print("="*60)
    print("TESTING: Burnley vs Man City Prediction")
    print("="*60)
    
    # Load models
    model1, model2 = load_prediction_models()
    
    # Predict
    result = advanced_predict_match("Burnley", "Man City", model1, model2, category="European Leagues")
    
    if result:
        print("\n--- RAW RESULT ---")
        print(f"Model Type: {result.get('model_type')}")
        print(f"Outcome: {result.get('outcome')}")
        print(f"Prediction Number: {result.get('prediction_number')}")
        
        if 'probabilities' in result:
            print(f"\nModel Probabilities (raw): {result['probabilities']}")
        
        if 'historical_probs' in result:
            print(f"Historical Probs (H2H): {result['historical_probs']}")
        
        # Process via views
        probs, outcome = process_prediction_probabilities(result)
        
        print("\n--- PROCESSED (what goes to URL) ---")
        print(f"Probabilities: {probs}")
        print(f"  Home: {probs.get('Home', 0)*100:.1f}%")
        print(f"  Draw: {probs.get('Draw', 0)*100:.1f}%")
        print(f"  Away: {probs.get('Away', 0)*100:.1f}%")
        print(f"Outcome: {outcome}")
        
        # Check if it's fallback
        home_val = probs.get('Home', 0)
        draw_val = probs.get('Draw', 0)
        away_val = probs.get('Away', 0)
        
        is_fallback = (abs(home_val - 0.33) < 0.02 and 
                      abs(draw_val - 0.33) < 0.02 and 
                      abs(away_val - 0.34) < 0.02)
        
        print(f"\nIs Fallback? {is_fallback}")
        
        if is_fallback:
            print("⚠️ WARNING: System is returning fallback probabilities!")
            print("This suggests the model prediction failed or returned None")
    else:
        print("❌ advanced_predict_match returned None")

if __name__ == "__main__":
    test_burnley_city()
