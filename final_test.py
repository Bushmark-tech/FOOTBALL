#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final comprehensive test - verify all fixes are working.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

print("\n" + "="*70)
print("  FINAL VERIFICATION TEST")
print("="*70)

# Test 1: Man City data lookup
print("\n[1] Man City Data Lookup (ID-based matching)")
try:
    from predictor.analytics import get_team_recent_form_original, load_football_data
    data = load_football_data(dataset=1)
    form = get_team_recent_form_original("Man City", data, version="v1")
    
    # Check if it's real data (not generated fallback)
    if "Generated realistic form" in str(form):
        print("  ✗ FAIL: Still using generated form")
    else:
        print(f"  ✓ PASS: Real form data found: {form}")
except Exception as e:
    print(f"  ✗ FAIL: {e}")

# Test 2: Full prediction with real data
print("\n[2] Full Prediction (should use real data, not fallback)")
try:
    from predictor.views import load_prediction_models
    from predictor.analytics import advanced_predict_match
    
    model1, model2 = load_prediction_models()
    result = advanced_predict_match("Man City", "Liverpool", model1, model2)
    
    if result:
        model_type = result.get('model_type', '')
        if 'Fallback' in model_type:
            print(f"  ⚠ WARNING: Using fallback - {model_type}")
        else:
            print(f"  ✓ PASS: Prediction successful")
            print(f"    Model: {model_type}")
            print(f"    Outcome: {result.get('outcome')}")
            print(f"    Confidence: {result.get('confidence', 0):.1%}")
    else:
        print("  ✗ FAIL: Prediction returned None")
except Exception as e:
    print(f"  ✗ FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Double chance threshold
print("\n[3] Double Chance Logic (2% threshold)")
try:
    from predictor.views import calculate_double_chance
    
    # Test case: probabilities very close but not within 2%
    result = calculate_double_chance(0.36, 0.33, 0.31)  # 3% difference
    
    if result in ['1X', 'X2', '12']:
        print(f"  ⚠ WARNING: Showing double chance ({result}) for 3% diff")
    else:
        print(f"  ✓ PASS: Single outcome ({result}) for 3% diff")
    
    # Test case: extremely close (within 2%)
    result2 = calculate_double_chance(0.34, 0.33, 0.33)  # 1% difference
    print(f"    Very close probs (1% diff): {result2}")
    
except Exception as e:
    print(f"  ✗ FAIL: {e}")

# Test 4: Probability sum validation
print("\n[4] Probability Validation")
try:
    result = advanced_predict_match("Arsenal", "Chelsea", model1, model2)
    if result:
        probs = result.get('probabilities', {})
        prob_sum = sum(probs.values())
        
        if abs(prob_sum - 1.0) < 0.01:
            print(f"  ✓ PASS: Probabilities sum to {prob_sum:.4f}")
        else:
            print(f"  ✗ FAIL: Probabilities sum to {prob_sum:.4f} (should be ~1.0)")
    else:
        print("  ✗ FAIL: No prediction result")
except Exception as e:
    print(f"  ✗ FAIL: {e}")

print("\n" + "="*70)
print("  VERIFICATION COMPLETE")
print("="*70 + "\n")
