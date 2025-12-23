"""
Test Double Chance with real match predictions to see it in action.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
django.setup()

from predictor.analytics import advanced_predict_match
import pickle
import os

def load_models():
    """Load the trained models."""
    model1_path = os.path.join(os.path.dirname(__file__), 'models', 'model1.pkl')
    model2_path = os.path.join(os.path.dirname(__file__), 'models', 'model2.pkl')
    
    try:
        with open(model1_path, 'rb') as f:
            model1 = pickle.load(f)
        with open(model2_path, 'rb') as f:
            model2 = pickle.load(f)
        return model1, model2
    except Exception as e:
        print(f"Warning: Could not load models: {e}")
        return None, None

def test_real_matches():
    """Test double chance with real match scenarios."""
    
    print("=" * 80)
    print("TESTING DOUBLE CHANCE WITH REAL MATCH PREDICTIONS")
    print("=" * 80)
    print()
    
    # Load models
    print("Loading models...")
    model1, model2 = load_models()
    if model1 is None or model2 is None:
        print("❌ Could not load models. Exiting.")
        return
    print("✅ Models loaded successfully\n")
    
    # Test matches that might trigger double chance
    test_matches = [
        ("Manchester City", "Liverpool"),
        ("Barcelona", "Real Madrid"),
        ("Bayern Munich", "Borussia Dortmund"),
        ("Arsenal", "Chelsea"),
        ("PSG", "Marseille"),
        ("Juventus", "Inter Milan"),
        ("Atletico Madrid", "Sevilla"),
        ("Tottenham", "Manchester United"),
    ]
    
    double_chance_count = 0
    
    for home, away in test_matches:
        print(f"\n{'='*80}")
        print(f"Match: {home} vs {away}")
        print('='*80)
        
        try:
            result = advanced_predict_match(home, away, model1, model2)
            
            # Extract key information
            final_pred = result.get('final_prediction', 'N/A')
            category = result.get('category', 'N/A')
            probs = result.get('probabilities', {})
            
            print(f"\n📊 Probabilities:")
            print(f"   Home Win: {probs.get('Home Team Win', 0):.1f}%")
            print(f"   Draw:     {probs.get('Draw', 0):.1f}%")
            print(f"   Away Win: {probs.get('Away Team Win', 0):.1f}%")
            
            print(f"\n🎯 Final Prediction: {final_pred}")
            print(f"📁 Category: {category}")
            
            # Check if this is a double chance scenario
            if " or " in final_pred:
                print(f"\n⚠️  DOUBLE CHANCE DETECTED!")
                print(f"   This indicates the probabilities are very close")
                print(f"   Prediction covers two outcomes: {final_pred}")
                double_chance_count += 1
            else:
                print(f"\n✅ Clear prediction (no double chance)")
            
            # Show confidence level
            confidence = result.get('confidence', 0)
            print(f"💪 Confidence: {confidence:.1f}%")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {double_chance_count} out of {len(test_matches)} matches triggered Double Chance")
    print("=" * 80)
    
    print("\n📝 DOUBLE CHANCE EXPLANATION:")
    print("-" * 80)
    print("Double Chance occurs when:")
    print("  • Two outcomes have very similar probabilities (within 5%)")
    print("  • The model prediction differs from the tied outcomes")
    print("  • This provides a safer bet covering two possible results")
    print()
    print("Examples:")
    print("  • 'Home Team Win or Draw' - Covers home win OR draw")
    print("  • 'Away Team Win or Draw' - Covers away win OR draw")
    print("  • 'Home Team Win or Away Team Win' - Covers either team winning (no draw)")
    print()
    print("In the UI, double chance predictions are simplified:")
    print("  • 'Home or Draw' → Displayed as 'Home' (primary outcome)")
    print("  • 'Away or Draw' → Displayed as 'Away' (primary outcome)")
    print("=" * 80)


if __name__ == "__main__":
    test_real_matches()

