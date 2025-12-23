"""
Test script to verify Double Chance logic is working correctly.
This tests all scenarios where double chance should be triggered.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
django.setup()

from predictor.analytics import determine_final_prediction

def test_double_chance_scenarios():
    """Test all double chance scenarios."""
    
    print("=" * 80)
    print("TESTING DOUBLE CHANCE LOGIC")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "Home & Draw Tied - Model predicts Away",
            "model_pred": 0,  # Away
            "probs": {
                'Home Team Win': 40.0,
                'Draw': 40.0,
                'Away Team Win': 20.0
            },
            "expected": "Home Team Win or Draw",
            "description": "When Home and Draw are tied, and model predicts Away, should return double chance"
        },
        {
            "name": "Away & Draw Tied - Model predicts Home",
            "model_pred": 2,  # Home
            "probs": {
                'Home Team Win': 20.0,
                'Draw': 40.0,
                'Away Team Win': 40.0
            },
            "expected": "Away Team Win or Draw",
            "description": "When Away and Draw are tied, and model predicts Home, should return double chance"
        },
        {
            "name": "Home & Away Tied - Model predicts Draw",
            "model_pred": 1,  # Draw
            "probs": {
                'Home Team Win': 40.0,
                'Draw': 20.0,
                'Away Team Win': 40.0
            },
            "expected": "Home Team Win or Away Team Win",
            "description": "When Home and Away are tied, and model predicts Draw, should return double chance"
        },
        {
            "name": "Home & Draw Close - Model predicts Home",
            "model_pred": 2,  # Home
            "probs": {
                'Home Team Win': 38.0,
                'Draw': 37.0,
                'Away Team Win': 25.0
            },
            "expected": "Home Team Win",
            "description": "When Home and Draw are close, and model predicts Home (which is in the tie), use model"
        },
        {
            "name": "Clear Home Win - Model agrees",
            "model_pred": 2,  # Home
            "probs": {
                'Home Team Win': 60.0,
                'Draw': 25.0,
                'Away Team Win': 15.0
            },
            "expected": "Home Team Win",
            "description": "Clear winner, model agrees - no double chance"
        },
        {
            "name": "Clear Home Win - Model predicts Away",
            "model_pred": 0,  # Away
            "probs": {
                'Home Team Win': 60.0,
                'Draw': 25.0,
                'Away Team Win': 15.0
            },
            "expected": "Away Team Win",
            "description": "Model prediction prioritized even when historical shows clear winner"
        },
        {
            "name": "All Three Tied",
            "model_pred": 1,  # Draw
            "probs": {
                'Home Team Win': 33.0,
                'Draw': 34.0,
                'Away Team Win': 33.0
            },
            "expected": "Draw",
            "description": "When all three are tied, trust model prediction"
        },
        {
            "name": "Home & Draw Tied - Model predicts Draw",
            "model_pred": 1,  # Draw
            "probs": {
                'Home Team Win': 40.0,
                'Draw': 40.0,
                'Away Team Win': 20.0
            },
            "expected": "Draw",
            "description": "When Home and Draw are tied, and model predicts Draw (which is in the tie), use model"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Description: {test['description']}")
        print(f"  Model Prediction: {['Away', 'Draw', 'Home'][test['model_pred']]}")
        print(f"  Probabilities: Home={test['probs']['Home Team Win']:.1f}%, "
              f"Draw={test['probs']['Draw']:.1f}%, "
              f"Away={test['probs']['Away Team Win']:.1f}%")
        
        result = determine_final_prediction(test['model_pred'], test['probs'])
        
        print(f"  Expected: {test['expected']}")
        print(f"  Got:      {result}")
        
        if result == test['expected']:
            print("  ✅ PASSED")
            passed += 1
        else:
            print("  ❌ FAILED")
            failed += 1
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("✅ ALL DOUBLE CHANCE TESTS PASSED!")
        return True
    else:
        print(f"❌ {failed} TESTS FAILED - DOUBLE CHANCE LOGIC NEEDS REVIEW")
        return False


def test_double_chance_display():
    """Test how double chance predictions are displayed."""
    
    print("\n" + "=" * 80)
    print("TESTING DOUBLE CHANCE DISPLAY CONVERSION")
    print("=" * 80)
    print()
    
    # Test the conversion logic from double chance to single outcome
    double_chance_conversions = [
        ("Home Team Win or Draw", "Home", "Double chance Home/Draw -> Display as Home"),
        ("Away Team Win or Draw", "Away", "Double chance Away/Draw -> Display as Away"),
        ("Home Team Win or Away Team Win", "Home or Away", "Double chance Home/Away -> Use model to decide"),
    ]
    
    for dc_pred, display, description in double_chance_conversions:
        print(f"Double Chance: {dc_pred}")
        print(f"  Display as: {display}")
        print(f"  Logic: {description}")
        print()
    
    print("=" * 80)
    print("NOTE: Double chance predictions are converted to single outcomes for display")
    print("This ensures the UI shows a clear prediction while maintaining the logic")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("🔍 DOUBLE CHANCE LOGIC VERIFICATION")
    print("=" * 80)
    print()
    
    # Run the tests
    logic_passed = test_double_chance_scenarios()
    test_double_chance_display()
    
    print("\n" + "=" * 80)
    print("DOUBLE CHANCE LOGIC SUMMARY")
    print("=" * 80)
    print()
    print("Double Chance is triggered when:")
    print("  1. Home & Draw are tied/close AND model predicts Away")
    print("     → Returns: 'Home Team Win or Draw'")
    print()
    print("  2. Away & Draw are tied/close AND model predicts Home")
    print("     → Returns: 'Away Team Win or Draw'")
    print()
    print("  3. Home & Away are tied/close AND model predicts Draw")
    print("     → Returns: 'Home Team Win or Away Team Win'")
    print()
    print("Model Prediction Priority:")
    print("  - Model predictions are ALWAYS prioritized over historical probabilities")
    print("  - Even with clear historical winner, model can override")
    print()
    print("Display Logic:")
    print("  - Double chance predictions are converted to single outcomes for UI")
    print("  - 'Home or Draw' → Display as 'Home'")
    print("  - 'Away or Draw' → Display as 'Away'")
    print("  - 'Home or Away' → Use model prediction to decide")
    print("=" * 80)
    
    sys.exit(0 if logic_passed else 1)

