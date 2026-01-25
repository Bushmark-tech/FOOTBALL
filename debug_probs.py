
import os
import sys
import django
import pandas as pd
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor import analytics
from predictor.repositories import get_repository
from predictor.adapters import DataAdapterFactory

def debug_probabilities():
    print("DEBUGGING PROBABILITIES FOR Burnley vs Man City")
    print("="*50)
    
    repo = get_repository()
    
    # Check Dataset 2 (likely the one used for Model 2 / Default)
    print("\n--- Checking Dataset 2 (v2) ---")
    data_v2 = repo.get_dataset(2)
    
    if data_v2 is not None:
        print(f"Loaded v2 data: {len(data_v2)} rows")
        print(f"Columns: {list(data_v2.columns)}")
        adapter_v2 = DataAdapterFactory.create(data_v2, "v2")
        
        home_col = adapter_v2.get_home_column()
        away_col = adapter_v2.get_away_column()
        
        # Check team names
        unique_teams = pd.concat([data_v2[home_col].dropna(), data_v2[away_col].dropna()]).unique()
        unique_teams = [str(t).strip() for t in unique_teams]
        
        print(f"Unique teams: {len(unique_teams)}")
        
        # Look for variants
        city = [t for t in unique_teams if 'Man' in t and 'City' in t]
        burnley = [t for t in unique_teams if 'Burn' in t]
        print(f"Man City variants: {city}")
        print(f"Burnley variants: {burnley}")
        
        # Run calculation
        print("\n--- Running Calculation with Analytics Module ---")
        probs = analytics.calculate_probabilities_model2("Burnley", "Man City", data_v2, version="v2")
        print(f"Calculated Probs: {probs}")
        
        # Manual Check
        if city and burnley:
            home_team = "Burnley" # Target
            away_team = "Man City" # Target
            
            # Find matched names
            matched_home = analytics.find_team_in_data(home_team, data_v2, home_col)
            matched_away = analytics.find_team_in_data(away_team, data_v2, away_col)
            
            print(f"\nMatched Home: '{matched_home}'")
            print(f"Matched Away: '{matched_away}'")
            
            if matched_home and matched_away:
                home_matches, away_matches = repo.get_h2h_matches(matched_home, matched_away, data_v2, adapter_v2)
                
                print(f"Direct Matches (Burnley Home): {len(home_matches)}")
                if not home_matches.empty:
                    res_col = adapter_v2.get_result_column()
                    print(home_matches[[home_col, away_col, res_col, 'Date']].to_string())
                    print("Value counts:", home_matches[res_col].value_counts())
                
                print(f"\nReverse Matches (Man City Home): {len(away_matches)}")
                if not away_matches.empty:
                    res_col = adapter_v2.get_result_column()
                    print(away_matches[[home_col, away_col, res_col, 'Date']].to_string())
                    print("Value counts:", away_matches[res_col].value_counts())
    else:
        print("Dataset 2 failed to load.")

    # Check Dataset 1 just in case
    print("\n--- Checking Dataset 1 (v1) ---")
    data_v1 = repo.get_dataset(1)
    if data_v1 is not None:
        print(f"Loaded v1 data: {len(data_v1)} rows")
        # Just quick check of teams
        if 'HomeTeam' in data_v1.columns:
            unique_v1 = pd.concat([data_v1['HomeTeam'], data_v1['AwayTeam']]).unique()
            print(f"Man City variants v1: {[t for t in unique_v1 if 'Man' in str(t) and 'City' in str(t)]}")
            print(f"Burnley variants v1: {[t for t in unique_v1 if 'Burn' in str(t)]}")

if __name__ == "__main__":
    debug_probabilities()
