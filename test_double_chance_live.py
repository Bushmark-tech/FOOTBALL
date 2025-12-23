"""
Test with real team combinations that should trigger double chance.
We'll test evenly matched teams where probabilities should be close.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
django.setup()

from predictor.analytics import determine_final_prediction, calculate_probabilities_original
from predictor.models import Match
import pandas as pd

def test_evenly_matched_teams():
    """Test teams that should have close probabilities."""
    
    print("="*80)
    print("TESTING DOUBLE CHANCE WITH EVENLY MATCHED TEAMS")
    print("="*80)
    print()
    
    # Test cases with teams that should have close probabilities
    test_matches = [
        # Mid-table teams (usually close matches)
        ("Everton", "Aston Villa"),
        ("Crystal Palace", "Bournemouth"),
        ("Fulham", "Brentford"),
        ("Wolves", "Brighton"),
        
        # Similar strength teams
        ("Sevilla", "Villarreal"),
        ("Real Betis", "Athletic Bilbao"),
        ("Valencia", "Real Sociedad"),
        
        # Bundesliga mid-table
        ("Freiburg", "Hoffenheim"),
        ("Mainz", "Augsburg"),
        
        # Serie A evenly matched
        ("Torino", "Udinese"),
        ("Bologna", "Sassuolo"),
    ]
    
    double_chance_found = []
    
    for home, away in test_matches:
        print(f"\n{'='*80}")
        print(f"Testing: {home} vs {away}")
        print('='*80)
        
        # Try to calculate probabilities
        try:
            # Load data
            data = pd.DataFrame()  # Empty for fallback logic
            probs = calculate_probabilities_original(home, away, data, version="v1")
            
            print(f"\n📊 Probabilities:")
            print(f"   Home Win ({home}): {probs['Home Team Win']:.1f}%")
            print(f"   Draw: {probs['Draw']:.1f}%")
            print(f"   Away Win ({away}): {probs['Away Team Win']:.1f}%")
            
            # Check if close
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            max_prob = sorted_probs[0][1]
            second_prob = sorted_probs[1][1]
            diff = abs(max_prob - second_prob)
            
            print(f"\n🔍 Analysis:")
            print(f"   Highest: {sorted_probs[0][0]} = {sorted_probs[0][1]:.1f}%")
            print(f"   Second: {sorted_probs[1][0]} = {sorted_probs[1][1]:.1f}%")
            print(f"   Difference: {diff:.1f}%")
            
            if diff < 5.0:
                print(f"   ⚠️  CLOSE MATCH - Could trigger double chance!")
                
                # Test with different model predictions
                print(f"\n   Testing model predictions:")
                
                for model_pred, model_name in [(0, "Away"), (1, "Draw"), (2, "Home")]:
                    result = determine_final_prediction(model_pred, probs)
                    
                    if " or " in result:
                        print(f"      Model={model_name} → {result} ⚠️  DOUBLE CHANCE!")
                        double_chance_found.append({
                            'match': f"{home} vs {away}",
                            'probs': probs,
                            'model': model_name,
                            'result': result
                        })
                    else:
                        print(f"      Model={model_name} → {result}")
            else:
                print(f"   ✅ Clear winner - {diff:.1f}% gap")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("DOUBLE CHANCE RESULTS SUMMARY")
    print("="*80)
    print()
    
    if double_chance_found:
        print(f"✅ Found {len(double_chance_found)} double chance scenarios!\n")
        
        for i, dc in enumerate(double_chance_found, 1):
            print(f"{i}. {dc['match']}")
            print(f"   Probabilities: Home={dc['probs']['Home Team Win']:.1f}%, "
                  f"Draw={dc['probs']['Draw']:.1f}%, "
                  f"Away={dc['probs']['Away Team Win']:.1f}%")
            print(f"   Model: {dc['model']}")
            print(f"   Result: {dc['result']} ⚠️")
            print()
    else:
        print("❌ No double chance scenarios found in these matches.")
        print("   This might be because:")
        print("   • Teams have clear strength differences")
        print("   • Model predictions align with probabilities")
        print("   • Need to test with more evenly matched teams")
    
    print("="*80)


def test_manual_double_chance_scenarios():
    """Test with manually created close probability scenarios."""
    
    print("\n" + "="*80)
    print("MANUAL DOUBLE CHANCE SCENARIOS (GUARANTEED TO TRIGGER)")
    print("="*80)
    print()
    
    scenarios = [
        {
            "name": "Evenly Matched Derby",
            "home": "Team A",
            "away": "Team B",
            "probs": {
                'Home Team Win': 38.0,
                'Draw': 37.0,
                'Away Team Win': 25.0
            },
            "model": 1  # Draw
        },
        {
            "name": "Defensive Battle",
            "home": "Team C",
            "away": "Team D",
            "probs": {
                'Home Team Win': 30.0,
                'Draw': 42.0,
                'Away Team Win': 28.0
            },
            "model": 2  # Home
        },
        {
            "name": "Attack vs Attack",
            "home": "Team E",
            "away": "Team F",
            "probs": {
                'Home Team Win': 41.0,
                'Draw': 18.0,
                'Away Team Win': 41.0
            },
            "model": 1  # Draw
        },
        {
            "name": "Close Away Favorite",
            "home": "Team G",
            "away": "Team H",
            "probs": {
                'Home Team Win': 25.0,
                'Draw': 39.0,
                'Away Team Win': 36.0
            },
            "model": 2  # Home
        },
    ]
    
    double_chance_count = 0
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"Scenario: {scenario['name']}")
        print(f"Match: {scenario['home']} vs {scenario['away']}")
        print('='*80)
        
        probs = scenario['probs']
        model_pred = scenario['model']
        model_names = {0: "Away", 1: "Draw", 2: "Home"}
        
        print(f"\n📊 Probabilities:")
        print(f"   Home Win: {probs['Home Team Win']:.1f}%")
        print(f"   Draw: {probs['Draw']:.1f}%")
        print(f"   Away Win: {probs['Away Team Win']:.1f}%")
        print(f"\n🤖 Model Predicts: {model_names[model_pred]}")
        
        result = determine_final_prediction(model_pred, probs)
        
        print(f"\n🎯 Final Prediction: {result}")
        
        if " or " in result:
            print(f"\n💡 DOUBLE CHANCE TRIGGERED! ✅")
            print(f"   This covers TWO outcomes: {result}")
            double_chance_count += 1
        else:
            print(f"\n✅ Single outcome (no double chance)")
    
    print("\n" + "="*80)
    print(f"MANUAL SCENARIOS: {double_chance_count}/{len(scenarios)} triggered double chance")
    print("="*80)


if __name__ == "__main__":
    print("\n🔍 DOUBLE CHANCE - LIVE TESTING WITH REAL SCENARIOS\n")
    
    # Test with evenly matched teams
    test_evenly_matched_teams()
    
    # Test with manual scenarios (guaranteed to work)
    test_manual_double_chance_scenarios()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print("\nTo see double chance in the actual app:")
    print("  1. Go to http://127.0.0.1:8000")
    print("  2. Make a prediction with evenly matched teams")
    print("  3. Look for scenarios where probabilities are within 5%")
    print("\nDouble chance will show when:")
    print("  • Two outcomes have similar probabilities (within 5%)")
    print("  • Model prediction differs from the tied outcomes")
    print("="*80)

