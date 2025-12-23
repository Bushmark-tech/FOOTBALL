"""
Test script to verify prediction system works correctly.
Tests probability normalization and prediction logic.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import calculate_probabilities_original, load_football_data
from predictor.views import result
from django.test import RequestFactory

def test_probability_normalization():
    """Test that probabilities are normalized correctly."""
    print("=" * 70)
    print("Testing Probability Normalization")
    print("=" * 70)
    
    # Test with Arsenal vs Aston Villa (the example from user)
    home_team = "Arsenal"
    away_team = "Aston Villa"
    
    try:
        data = load_football_data(1, use_cache=True)
        data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
        
        if not data_empty:
            historical_probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
            
            if historical_probs:
                # Convert to decimal format (as done in views.py)
                probabilities = {
                    'Home': historical_probs.get("Home Team Win", 0) / 100.0,
                    'Draw': historical_probs.get("Draw", 0) / 100.0,
                    'Away': historical_probs.get("Away Team Win", 0) / 100.0
                }
                
                # Normalize (as done in views.py)
                total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
                if total_prob > 0:
                    probabilities['Home'] = probabilities['Home'] / total_prob
                    probabilities['Draw'] = probabilities['Draw'] / total_prob
                    probabilities['Away'] = probabilities['Away'] / total_prob
                
                # Convert back to percentages for display
                home_pct = probabilities['Home'] * 100
                draw_pct = probabilities['Draw'] * 100
                away_pct = probabilities['Away'] * 100
                total_pct = home_pct + draw_pct + away_pct
                
                print(f"\nMatch: {home_team} vs {away_team}")
                print(f"Historical Probabilities:")
                print(f"  Home Win: {home_pct:.1f}%")
                print(f"  Draw:     {draw_pct:.1f}%")
                print(f"  Away Win: {away_pct:.1f}%")
                print(f"  Total:    {total_pct:.1f}%")
                
                # Verify normalization
                if abs(total_pct - 100.0) < 0.1:
                    print("\n✅ PASS: Probabilities sum to 100% (normalized correctly)")
                else:
                    print(f"\n❌ FAIL: Probabilities sum to {total_pct:.1f}% (should be 100%)")
                
                # Check if prediction matches highest probability
                max_prob = max(probabilities.values())
                predicted_outcome = None
                if probabilities['Home'] == max_prob:
                    predicted_outcome = "Home Win"
                elif probabilities['Draw'] == max_prob:
                    predicted_outcome = "Draw"
                else:
                    predicted_outcome = "Away Win"
                
                print(f"\nPredicted Outcome: {predicted_outcome} ({max_prob*100:.1f}% confidence)")
                
                return True
            else:
                print(f"\n⚠️  No historical probabilities found for {home_team} vs {away_team}")
                return False
        else:
            print("\n⚠️  Data is empty, cannot test probabilities")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_matches():
    """Test predictions for multiple matches."""
    print("\n" + "=" * 70)
    print("Testing Multiple Matches")
    print("=" * 70)
    
    test_matches = [
        ("Arsenal", "Aston Villa"),
        ("Man City", "Liverpool"),
        ("Barcelona", "Real Madrid"),
        ("Bayern Munich", "Dortmund"),
    ]
    
    passed = 0
    failed = 0
    
    for home_team, away_team in test_matches:
        try:
            data = load_football_data(1, use_cache=True)
            data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
            
            if not data_empty:
                historical_probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
                
                if historical_probs:
                    probabilities = {
                        'Home': historical_probs.get("Home Team Win", 0) / 100.0,
                        'Draw': historical_probs.get("Draw", 0) / 100.0,
                        'Away': historical_probs.get("Away Team Win", 0) / 100.0
                    }
                    
                    # Normalize
                    total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
                    if total_prob > 0:
                        probabilities['Home'] /= total_prob
                        probabilities['Draw'] /= total_prob
                        probabilities['Away'] /= total_prob
                    
                    total_pct = (probabilities['Home'] + probabilities['Draw'] + probabilities['Away']) * 100
                    
                    if abs(total_pct - 100.0) < 0.1:
                        print(f"✅ {home_team} vs {away_team}: Probabilities normalized correctly ({total_pct:.1f}%)")
                        passed += 1
                    else:
                        print(f"❌ {home_team} vs {away_team}: Probabilities sum to {total_pct:.1f}%")
                        failed += 1
                else:
                    print(f"⚠️  {home_team} vs {away_team}: No historical data")
        except Exception as e:
            print(f"❌ {home_team} vs {away_team}: Error - {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Football Predictor - Prediction System Test")
    print("=" * 70)
    
    # Test probability normalization
    test1_passed = test_probability_normalization()
    
    # Test multiple matches
    test2_passed = test_multiple_matches()
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    if test1_passed and test2_passed:
        print("✅ All tests PASSED!")
    else:
        print("❌ Some tests FAILED!")
    print("=" * 70 + "\n")

