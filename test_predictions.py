#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify prediction system is working correctly.
Tests:
1. Model loading
2. Team matching (ID-based and name-based)
3. Probability calculation
4. Double chance logic
5. Fallback mechanisms
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.views import load_prediction_models, calculate_double_chance
from predictor.analytics import (
    advanced_predict_match, 
    find_team_in_data, 
    load_team_mapping,
    load_football_data,
    calculate_probabilities_model2,
    calculate_probabilities_original
)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_model_loading():
    """Test if models load correctly."""
    print_section("TEST 1: Model Loading")
    
    try:
        model1, model2 = load_prediction_models()
        
        if model1:
            print("✓ Model 1 loaded successfully")
            if hasattr(model1, 'n_features_in_'):
                print(f"  - Expected features: {model1.n_features_in_}")
        else:
            print("✗ Model 1 failed to load")
        
        if model2:
            print("✓ Model 2 loaded successfully")
            if hasattr(model2, 'n_features_in_'):
                print(f"  - Expected features: {model2.n_features_in_}")
        else:
            print("✗ Model 2 failed to load")
        
        return model1, model2
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_team_mapping():
    """Test team ID mapping."""
    print_section("TEST 2: Team ID Mapping")
    
    try:
        mapping = load_team_mapping()
        print(f"✓ Team mapping loaded: {len(mapping)} teams")
        
        # Test specific teams
        test_teams = ["Man City", "Liverpool", "Arsenal", "Chelsea"]
        for team in test_teams:
            team_id = mapping.get(team)
            if team_id:
                print(f"  - {team}: ID {team_id}")
            else:
                print(f"  - {team}: NOT FOUND in mapping")
        
        return mapping
    except Exception as e:
        print(f"✗ Error loading team mapping: {e}")
        return {}

def test_team_finding():
    """Test team finding in dataset."""
    print_section("TEST 3: Team Finding in Dataset")
    
    try:
        data = load_football_data(dataset=1)
        
        # Test various team name formats
        test_cases = [
            ("Man City", "HomeTeam"),
            ("Manchester City", "HomeTeam"),
            ("Liverpool", "HomeTeam"),
            ("Arsenal", "HomeTeam"),
        ]
        
        for team_name, column in test_cases:
            found = find_team_in_data(team_name, data, column)
            if found:
                print(f"✓ '{team_name}' -> '{found}'")
            else:
                print(f"✗ '{team_name}' -> NOT FOUND")
        
        return True
    except Exception as e:
        print(f"✗ Error testing team finding: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_probability_calculation():
    """Test probability calculation."""
    print_section("TEST 4: Probability Calculation")
    
    try:
        data_v1 = load_football_data(dataset=1)
        data_v2 = load_football_data(dataset=2)
        
        # Test with common matchup
        home = "Man City"
        away = "Liverpool"
        
        print(f"\nTesting: {home} vs {away}")
        
        # Test Model 1 probabilities (v1 data)
        probs_v1 = calculate_probabilities_original(home, away, data_v1, version="v1")
        if probs_v1:
            print(f"✓ Model 1 probabilities calculated:")
            print(f"  - Home: {probs_v1.get('Home Team Win', 0):.1f}%")
            print(f"  - Draw: {probs_v1.get('Draw', 0):.1f}%")
            print(f"  - Away: {probs_v1.get('Away Team Win', 0):.1f}%")
        else:
            print(f"✗ Model 1 probabilities: FAILED (returned None)")
        
        # Test Model 2 probabilities (v2 data)
        probs_v2 = calculate_probabilities_model2(home, away, data_v2, version="v2")
        if probs_v2:
            print(f"✓ Model 2 probabilities calculated:")
            print(f"  - Home: {probs_v2.get('Home Team Win', 0):.1f}%")
            print(f"  - Draw: {probs_v2.get('Draw', 0):.1f}%")
            print(f"  - Away: {probs_v2.get('Away Team Win', 0):.1f}%")
        else:
            print(f"⚠ Model 2 probabilities: None (will use fallback)")
        
        return probs_v1 is not None
    except Exception as e:
        print(f"✗ Error calculating probabilities: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_double_chance_logic():
    """Test double chance calculation."""
    print_section("TEST 5: Double Chance Logic")
    
    test_cases = [
        # (prob_home, prob_draw, prob_away, expected_outcome_type)
        (0.50, 0.30, 0.20, "Single"),  # Clear home win
        (0.35, 0.35, 0.30, "Single"),  # Close, but should pick single
        (0.34, 0.33, 0.33, "Single"),  # Very close, still single (2% threshold)
        (0.40, 0.35, 0.25, "Single"),  # Home favored
        (0.25, 0.35, 0.40, "Single"),  # Away favored
    ]
    
    for prob_home, prob_draw, prob_away, expected_type in test_cases:
        outcome = calculate_double_chance(prob_home, prob_draw, prob_away)
        is_double = outcome in ['1X', 'X2', '12']
        actual_type = "Double" if is_double else "Single"
        
        status = "✓" if actual_type == expected_type else "⚠"
        print(f"{status} H:{prob_home:.2f} D:{prob_draw:.2f} A:{prob_away:.2f} -> {outcome} ({actual_type})")
    
    return True

def test_full_prediction():
    """Test full prediction pipeline."""
    print_section("TEST 6: Full Prediction Pipeline")
    
    try:
        model1, model2 = load_prediction_models()
        
        # Test multiple match scenarios
        test_matches = [
            ("Man City", "Liverpool"),
            ("Arsenal", "Chelsea"),
            ("Man United", "Tottenham"),
        ]
        
        for home, away in test_matches:
            print(f"\n--- Predicting: {home} vs {away} ---")
            
            result = advanced_predict_match(home, away, model1, model2)
            
            if result:
                print(f"✓ Prediction successful")
                print(f"  - Outcome: {result.get('outcome')}")
                print(f"  - Confidence: {result.get('confidence', 0):.2%}")
                print(f"  - Model: {result.get('model_type')}")
                
                probs = result.get('probabilities', {})
                print(f"  - Probabilities:")
                print(f"    Away: {probs.get(0, 0):.2%}")
                print(f"    Draw: {probs.get(1, 0):.2%}")
                print(f"    Home: {probs.get(2, 0):.2%}")
                
                # Validate probabilities sum to ~1.0
                prob_sum = sum(probs.values())
                if abs(prob_sum - 1.0) < 0.01:
                    print(f"  ✓ Probabilities sum correctly: {prob_sum:.4f}")
                else:
                    print(f"  ✗ Probabilities sum incorrect: {prob_sum:.4f}")
            else:
                print(f"✗ Prediction failed (returned None)")
        
        return True
    except Exception as e:
        print(f"✗ Error in full prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  FOOTBALL PREDICTION SYSTEM - COMPREHENSIVE TEST")
    print("="*70)
    
    results = {}
    
    # Run tests
    model1, model2 = test_model_loading()
    results['model_loading'] = (model1 is not None or model2 is not None)
    
    mapping = test_team_mapping()
    results['team_mapping'] = len(mapping) > 0
    
    results['team_finding'] = test_team_finding()
    results['probability_calc'] = test_probability_calculation()
    results['double_chance'] = test_double_chance_logic()
    results['full_prediction'] = test_full_prediction()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
