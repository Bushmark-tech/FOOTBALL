import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models, process_prediction_probabilities

def test_arsenal_liverpool():
    print("="*60)
    print("TESTING: Arsenal vs Liverpool")
    print("="*60)
    
    # Load models
    model1, model2 = load_prediction_models()
    
    # Predict
    result = advanced_predict_match("Arsenal", "Liverpool", model1, model2, category="European Leagues")
    
    if result:
        print("\n--- RAW RESULT ---")
        print(f"Model Type: {result.get('model_type')}")
        print(f"Outcome: {result.get('outcome')}")
        print(f"Prediction Number: {result.get('prediction_number')}")
        print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
        
        if 'probabilities' in result:
            probs = result['probabilities']
            print(f"\nModel Probabilities (blended):")
            print(f"  Home (Arsenal): {probs.get(2, 0)*100:.1f}%")
            print(f"  Draw: {probs.get(1, 0)*100:.1f}%")
            print(f"  Away (Liverpool): {probs.get(0, 0)*100:.1f}%")
        
        if 'historical_probs' in result:
            h2h = result['historical_probs']
            print(f"\nHistorical H2H Probabilities:")
            print(f"  Arsenal Win: {h2h.get('Home Team Win', 0):.1f}%")
            print(f"  Draw: {h2h.get('Draw', 0):.1f}%")
            print(f"  Liverpool Win: {h2h.get('Away Team Win', 0):.1f}%")
        
        # Process via views
        probs_processed, outcome = process_prediction_probabilities(result)
        
        print("\n--- PROCESSED (what goes to URL) ---")
        print(f"Outcome: {outcome}")
        print(f"Probabilities:")
        print(f"  Home (Arsenal): {probs_processed.get('Home', 0)*100:.1f}%")
        print(f"  Draw: {probs_processed.get('Draw', 0)*100:.1f}%")
        print(f"  Away (Liverpool): {probs_processed.get('Away', 0)*100:.1f}%")
        
        # Check if it should be double chance
        home_val = probs_processed.get('Home', 0)
        draw_val = probs_processed.get('Draw', 0)
        away_val = probs_processed.get('Away', 0)
        
        max_prob = max(home_val, draw_val, away_val)
        sorted_vals = sorted([home_val, draw_val, away_val], reverse=True)
        prob_diff = sorted_vals[0] - sorted_vals[1]
        
        print(f"\nDouble Chance Analysis:")
        print(f"  Max probability: {max_prob*100:.1f}%")
        print(f"  Difference (1st - 2nd): {prob_diff*100:.1f}%")
        print(f"  Should use double chance? {prob_diff < 0.08 or max_prob < 0.45}")
        
    else:
        print("❌ advanced_predict_match returned None")

if __name__ == "__main__":
    test_arsenal_liverpool()
