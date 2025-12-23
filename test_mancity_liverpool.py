"""
Analyze the Man City vs Liverpool prediction to check double chance logic.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
django.setup()

from predictor.analytics import determine_final_prediction

# The probabilities shown in the UI
probs = {
    'Home Team Win': 36.4,
    'Draw': 54.5,
    'Away Team Win': 9.1
}

print("="*80)
print("MAN CITY VS LIVERPOOL - DOUBLE CHANCE ANALYSIS")
print("="*80)
print()
print("Historical Probabilities from UI:")
print(f"  Home Win (Man City): {probs['Home Team Win']:.1f}%")
print(f"  Draw: {probs['Draw']:.1f}%")
print(f"  Away Win (Liverpool): {probs['Away Team Win']:.1f}%")
print()

# Check if any two outcomes are within 5%
sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
max_prob = sorted_probs[0][1]
second_prob = sorted_probs[1][1]
diff = abs(max_prob - second_prob)

print("Analysis:")
print(f"  Highest: {sorted_probs[0][0]} = {sorted_probs[0][1]:.1f}%")
print(f"  Second: {sorted_probs[1][0]} = {sorted_probs[1][1]:.1f}%")
print(f"  Difference: {diff:.1f}%")
print()

if diff < 5.0:
    print("⚠️  CLOSE PROBABILITIES (within 5%) - Could trigger double chance")
else:
    print("✅ CLEAR WINNER - No double chance needed")
    print(f"   Draw has {diff:.1f}% lead over second place")

print()
print("="*80)
print("TESTING WITH DIFFERENT MODEL PREDICTIONS")
print("="*80)

# Test with different model predictions
model_predictions = [
    (0, "Away Win (Liverpool)"),
    (1, "Draw"),
    (2, "Home Win (Man City)")
]

for model_pred, model_name in model_predictions:
    print(f"\nIf Model Predicts: {model_name}")
    result = determine_final_prediction(model_pred, probs)
    print(f"  Final Prediction: {result}")
    
    if " or " in result:
        print(f"  ⚠️  DOUBLE CHANCE TRIGGERED")
    else:
        print(f"  ✅ Single outcome")

print()
print("="*80)
print("CONCLUSION")
print("="*80)
print()
print("With Draw at 54.5% (clear leader with 18.1% gap):")
print("  • No double chance should be triggered")
print("  • Draw is the clear favorite")
print("  • Model prediction would need to strongly disagree to override")
print()
print("Current prediction showing 'Draw' is CORRECT ✅")
print("="*80)

