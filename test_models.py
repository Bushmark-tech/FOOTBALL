"""
Test script to run Model1 and Model2 predictions.
This script demonstrates how the models make predictions.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
import json
import os
import joblib
import pickle


def load_models():
    """Load Model1 and Model2 from files."""
    model1 = None
    model2 = None
    
    # Define model paths - models are in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model1_path = os.path.join(script_dir, 'models', 'model1.pkl')
    model2_path = os.path.join(script_dir, 'models', 'model2.pkl')
    
    # Try to load Model1
    if os.path.exists(model1_path):
        try:
            model1 = joblib.load(model1_path)
            print("✓ Model1 loaded successfully")
        except Exception as e:
            try:
                with open(model1_path, 'rb') as f:
                    model1 = pickle.load(f)
                print("✓ Model1 loaded successfully (pickle)")
            except Exception as e2:
                print(f"⚠ Model1 loading error: {e2}")
    else:
        print(f"⚠ Model1 file not found at: {model1_path}")
    
    # Try to load Model2
    if os.path.exists(model2_path):
        try:
            # Try model2_loader first
            try:
                from predictor.model2_loader import load_model2_compatible
                model2, method = load_model2_compatible(model2_path)
                if model2:
                    print(f"✓ Model2 loaded successfully ({method})")
            except ImportError:
                # Fallback to direct loading
                try:
                    model2 = joblib.load(model2_path)
                    print("✓ Model2 loaded successfully (joblib)")
                except Exception:
                    with open(model2_path, 'rb') as f:
                        model2 = pickle.load(f)
                    print("✓ Model2 loaded successfully (pickle)")
        except Exception as e:
            print(f"⚠ Model2 loading error: {e}")
    else:
        print(f"⚠ Model2 file not found at: {model2_path}")
    
    return model1, model2


def test_model_predictions():
    """Test both Model1 and Model2 with sample teams."""
    
    print("=" * 70)
    print("FOOTBALL PREDICTION MODEL TEST")
    print("=" * 70)
    print()
    
    # Load models
    print("Loading models...")
    model1, model2 = load_models()
    
    if not model1 and not model2:
        print("\n⚠ No models loaded. Predictions will use fallback methods.")
    print()
    
    print()
    
    # Test Model1 (European League teams)
    print("-" * 70)
    print("TEST 1: Model1 Prediction (European League Teams)")
    print("-" * 70)
    test_cases_model1 = [
        ('Arsenal', 'Chelsea', 'European Leagues'),
        ('Man City', 'Liverpool', 'European Leagues'),
        ('Barcelona', 'Real Madrid', 'European Leagues'),
    ]
    
    for home_team, away_team, category in test_cases_model1:
        print(f"\nMatch: {home_team} vs {away_team}")
        print(f"Category: {category}")
        
        try:
            result = advanced_predict_match(home_team, away_team, model1, model2)
            
            if result:
                print(f"  Model Type: {result.get('model_type', 'Unknown')}")
                print(f"  Predicted Outcome: {result.get('outcome', 'Unknown')}")
                
                probs = result.get('probabilities', {})
                if isinstance(probs, dict):
                    prob_home = probs.get(0, probs.get('Home', 0))
                    prob_draw = probs.get(1, probs.get('Draw', 0))
                    prob_away = probs.get(2, probs.get('Away', 0))
                    
                    print(f"  Probabilities:")
                    print(f"    Home Win: {prob_home:.2%}")
                    print(f"    Draw: {prob_draw:.2%}")
                    print(f"    Away Win: {prob_away:.2%}")
                
                confidence = result.get('confidence', 0)
                print(f"  Confidence: {confidence:.2%}")
                
                if result.get('model1_prediction') is not None:
                    print(f"  Model1 Prediction: {result.get('model1_prediction')}")
                if result.get('model2_prediction') is not None:
                    print(f"  Model2 Prediction: {result.get('model2_prediction')}")
            else:
                print("  ⚠ No prediction result returned")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print()
    
    # Test Model2 (Other category teams)
    print("-" * 70)
    print("TEST 2: Model2 Prediction (Other Category Teams)")
    print("-" * 70)
    test_cases_model2 = [
        ('Basel', 'Zurich', 'Others'),
        ('Salzburg', 'LASK', 'Others'),
        ('FC Copenhagen', 'Brondby', 'Others'),
    ]
    
    for home_team, away_team, category in test_cases_model2:
        print(f"\nMatch: {home_team} vs {away_team}")
        print(f"Category: {category}")
        
        try:
            result = advanced_predict_match(home_team, away_team, model1, model2)
            
            if result:
                print(f"  Model Type: {result.get('model_type', 'Unknown')}")
                print(f"  Predicted Outcome: {result.get('outcome', 'Unknown')}")
                
                probs = result.get('probabilities', {})
                if isinstance(probs, dict):
                    prob_home = probs.get(0, probs.get('Home', 0))
                    prob_draw = probs.get(1, probs.get('Draw', 0))
                    prob_away = probs.get(2, probs.get('Away', 0))
                    
                    print(f"  Probabilities:")
                    print(f"    Home Win: {prob_home:.2%}")
                    print(f"    Draw: {prob_draw:.2%}")
                    print(f"    Away Win: {prob_away:.2%}")
                
                confidence = result.get('confidence', 0)
                print(f"  Confidence: {confidence:.2%}")
                
                if result.get('model1_prediction') is not None:
                    print(f"  Model1 Prediction: {result.get('model1_prediction')}")
                if result.get('model2_prediction') is not None:
                    print(f"  Model2 Prediction: {result.get('model2_prediction')}")
                
                if result.get('total_goals_prediction'):
                    print(f"  Total Goals Prediction: {result.get('total_goals_prediction'):.2f}")
            else:
                print("  ⚠ No prediction result returned")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    test_model_predictions()

