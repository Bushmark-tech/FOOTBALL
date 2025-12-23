"""Test Others category teams to identify issues."""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import (
    calculate_probabilities_original, 
    get_team_recent_form_original,
    load_football_data
)
import pandas as pd

def test_others_category():
    """Test Others category teams to find issues."""
    print("=" * 70)
    print("Testing Others Category Teams - Issue Detection")
    print("=" * 70)
    
    # Test Switzerland League teams
    test_teams = ["Grasshoppers", "Lausanne", "Basel", "Zurich", "Young Boys", "Lugano"]
    
    print("\n1. Checking Dataset 2 (for Others category):")
    data2 = load_football_data(2, use_cache=True)
    print(f"   Dataset 2 rows: {len(data2)}")
    
    if hasattr(data2, 'columns') and len(data2.columns) > 0:
        if 'HomeTeam' in data2.columns:
            home_col, away_col = 'HomeTeam', 'AwayTeam'
        elif 'Home' in data2.columns:
            home_col, away_col = 'Home', 'Away'
        else:
            print("   ❌ Cannot find team columns in dataset 2")
            return
        
        # Check what teams are actually in dataset 2
        all_teams_d2 = set(data2[home_col].astype(str).unique()) | set(data2[away_col].astype(str).unique())
        print(f"   Unique teams in dataset 2: {len(all_teams_d2)}")
        print(f"   Sample teams: {list(all_teams_d2)[:10]}")
        
        # Check if Switzerland teams are in dataset 2
        swiss_teams_found = []
        for team in test_teams:
            matches = data2[
                (data2[home_col].astype(str).str.contains(team, case=False, na=False)) |
                (data2[away_col].astype(str).str.contains(team, case=False, na=False))
            ]
            if len(matches) > 0:
                swiss_teams_found.append(team)
                print(f"   ✅ {team}: {len(matches)} matches found")
            else:
                print(f"   ❌ {team}: NO matches found")
        
        if len(swiss_teams_found) == 0:
            print("\n   ⚠️  PROBLEM: No Switzerland teams found in dataset 2!")
            print("   → Forms will be hash-based, not from real data")
            print("   → Historical probabilities will be form-based, not H2H")
    
    print("\n2. Checking Dataset 1 (might have Switzerland data):")
    data1 = load_football_data(1, use_cache=True)
    print(f"   Dataset 1 rows: {len(data1)}")
    
    if hasattr(data1, 'columns') and len(data1.columns) > 0:
        if 'HomeTeam' in data1.columns:
            home_col1, away_col1 = 'HomeTeam', 'AwayTeam'
        else:
            home_col1, away_col1 = 'Home', 'Away'
        
        # Check if Switzerland teams are in dataset 1
        swiss_in_d1 = []
        for team in test_teams:
            matches = data1[
                (data1[home_col1].astype(str).str.contains(team, case=False, na=False)) |
                (data1[away_col1].astype(str).str.contains(team, case=False, na=False))
            ]
            if len(matches) > 0:
                swiss_in_d1.append(team)
                print(f"   ✅ {team}: {len(matches)} matches in dataset 1")
        
        if len(swiss_in_d1) > 0:
            print(f"\n   ⚠️  FOUND: {len(swiss_in_d1)} Switzerland teams in dataset 1!")
            print("   → Should use dataset 1 for form calculation")
    
    print("\n3. Testing Form Calculation:")
    for team in test_teams[:3]:  # Test first 3
        print(f"\n   {team}:")
        form_d2 = get_team_recent_form_original(team, data2, version="v1")
        print(f"      Dataset 2 form: {form_d2}")
        
        if len(swiss_in_d1) > 0:
            form_d1 = get_team_recent_form_original(team, data1, version="v1")
            print(f"      Dataset 1 form: {form_d1}")
            if form_d1 != form_d2:
                print(f"      ⚠️  DIFFERENT! Should use dataset 1")
    
    print("\n4. Testing Historical Probabilities:")
    home_team = "Grasshoppers"
    away_team = "Lausanne"
    
    print(f"\n   {home_team} vs {away_team}:")
    probs_d2 = calculate_probabilities_original(home_team, away_team, data2, version="v1")
    print(f"      Dataset 2: {probs_d2}")
    
    if len(swiss_in_d1) > 0:
        probs_d1 = calculate_probabilities_original(home_team, away_team, data1, version="v1")
        print(f"      Dataset 1: {probs_d1}")
        if probs_d1 != probs_d2:
            print(f"      ⚠️  DIFFERENT! Should use dataset 1")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    if len(swiss_in_d1) > 0:
        print("→ Switzerland teams are in dataset 1, not dataset 2")
        print("→ Need to check dataset 1 for form calculation for Others teams")
    else:
        print("→ Switzerland teams not found in either dataset")
        print("→ Forms and probabilities will use fallback methods")
    print("=" * 70)

if __name__ == "__main__":
    test_others_category()







