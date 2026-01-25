import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models

print("="*70)
print("TESTING INTELLIGENT FORM WEIGHTING")
print("="*70)
print("\nTest Case: Liverpool vs Arsenal")
print("  Liverpool Form: DDWWW (60% win rate)")
print("  Arsenal Form: WWWWW (100% win rate - PERFECT!)")
print("\nExpected: Arsenal should be favored or get double chance")
print("="*70)

# Load models
model1, model2 = load_prediction_models()

# Test Liverpool vs Arsenal
result = advanced_predict_match("Liverpool", "Arsenal", model1, model2)

if result:
    outcome = result.get('outcome')
    confidence = result.get('confidence', 0)
    probs = result.get('probabilities', {})
    
    print(f"\nRESULT:")
    print(f"  Outcome: {outcome}")
    print(f"  Confidence: {confidence*100:.1f}%")
    print(f"\n  Probabilities:")
    print(f"    Liverpool (Home): {probs.get(2, 0)*100:.1f}%")
    print(f"    Draw: {probs.get(1, 0)*100:.1f}%")
    print(f"    Arsenal (Away): {probs.get(0, 0)*100:.1f}%")
    
    # Check if prediction makes sense
    arsenal_prob = probs.get(0, 0)
    liverpool_prob = probs.get(2, 0)
    
    print(f"\n  Analysis:")
    if arsenal_prob > liverpool_prob:
        print(f"    [OK] Arsenal favored ({arsenal_prob*100:.1f}% > {liverpool_prob*100:.1f}%) - CORRECT!")
    elif outcome in ['X2', 'Draw or Arsenal']:
        print(f"    [OK] Double chance includes Arsenal - REASONABLE!")
    else:
        print(f"    [WARNING] Liverpool favored despite Arsenal's perfect form - May need adjustment")
else:
    print("  ERROR: No result returned")

print("\n" + "="*70)
