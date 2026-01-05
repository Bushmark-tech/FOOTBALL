#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to verify prediction system changes.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

print("\n" + "="*70)
print("  TESTING PREDICTION SYSTEM IMPROVEMENTS")
print("="*70)

# Test 1: Model Loading
print("\n[TEST 1] Model Loading...")
try:
    from predictor.views import load_prediction_models
    model1, model2 = load_prediction_models()
    
    if model1:
        print("  ✓ Model 1 loaded")
    else:
        print("  ✗ Model 1 failed")
    
    if model2:
        print("  ✓ Model 2 loaded")
    else:
        print("  ⚠ Model 2 not loaded (may use fallback)")
except Exception as e:
    print(f"  ✗ Error: {e}")
    model1, model2 = None, None

# Test 2: Team ID Mapping
print("\n[TEST 2] Team ID Mapping...")
try:
    from predictor.analytics import load_team_mapping
    mapping = load_team_mapping()
    print(f"  ✓ Loaded {len(mapping)} teams")
    
    # Check specific teams
    test_teams = ["Man City", "Liverpool", "Arsenal"]
    for team in test_teams:
        if team in mapping:
            print(f"  ✓ {team}: ID {mapping[team]}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Team Finding (ID-based matching)
print("\n[TEST 3] Team Finding with ID Matching...")
try:
    from predictor.analytics import find_team_in_data, load_football_data
    data = load_football_data(dataset=1)
    
    test_cases = [
        ("Man City", "HomeTeam"),
        ("Manchester City", "HomeTeam"),
        ("Liverpool", "HomeTeam"),
    ]
    
    for team, col in test_cases:
        found = find_team_in_data(team, data, col)
        if found:
            print(f"  ✓ '{team}' -> '{found}'")
        else:
            print(f"  ✗ '{team}' not found")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Double Chance Thresholds
print("\n[TEST 4] Double Chance Logic (2% threshold)...")
try:
    from predictor.views import calculate_double_chance
    
    test_cases = [
        (0.50, 0.30, 0.20, "Home"),     # Clear home
        (0.40, 0.35, 0.25, "Home"),     # Home favored
        (0.35, 0.34, 0.31, "Home"),     # Very close - should be single
        (0.34, 0.33, 0.33, "Home"),     # Extremely close
    ]
    
    for h, d, a, expected in test_cases:
        result = calculate_double_chance(h, d, a)
        is_double = result in ['1X', 'X2', '12']
        status = "⚠ DOUBLE" if is_double else "✓ Single"
        print(f"  {status}: H:{h:.2f} D:{d:.2f} A:{a:.2f} -> {result}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 5: Full Prediction
print("\n[TEST 5] Full Prediction Pipeline...")
try:
    from predictor.analytics import advanced_predict_match
    
    home, away = "Man City", "Liverpool"
    print(f"  Testing: {home} vs {away}")
    
    result = advanced_predict_match(home, away, model1, model2)
    
    if result:
        outcome = result.get('outcome')
        confidence = result.get('confidence', 0)
        model_type = result.get('model_type', 'Unknown')
        probs = result.get('probabilities', {})
        
        print(f"  ✓ Prediction: {outcome}")
        print(f"    Confidence: {confidence:.1%}")
        print(f"    Model: {model_type}")
        print(f"    Probabilities:")
        print(f"      Away: {probs.get(0, 0):.1%}")
        print(f"      Draw: {probs.get(1, 0):.1%}")
        print(f"      Home: {probs.get(2, 0):.1%}")
        
        # Validate
        prob_sum = sum(probs.values())
        if abs(prob_sum - 1.0) < 0.01:
            print(f"    ✓ Probabilities sum: {prob_sum:.4f}")
        else:
            print(f"    ✗ Probabilities sum: {prob_sum:.4f} (should be ~1.0)")
    else:
        print(f"  ✗ Prediction failed")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70 + "\n")
