
import os
import sys
import django
import pandas as pd
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.repositories import get_repository
from predictor.adapters import DataAdapterFactory

def debug_v1_matches():
    print("DEBUGGING V1 MATCHES (ID 70 vs ID 233)")
    print("="*50)
    
    repo = get_repository()
    data_v1 = repo.get_dataset(1)
    
    if data_v1 is not None:
        adapter = DataAdapterFactory.create(data_v1, "v1")
        home_col = adapter.get_home_column()
        away_col = adapter.get_away_column()
        res_col = adapter.get_result_column()
        
        # ID 70 (Burnley) vs ID 233 (Man City)
        home_id = 70
        away_id = 233
        
        # Direction 1
        mask1 = (data_v1[home_col] == home_id) & (data_v1[away_col] == away_id)
        matches1 = data_v1[mask1]
        
        print(f"\nMatches: ID {home_id} (Home) vs ID {away_id} (Away)")
        print(f"Count: {len(matches1)}")
        if not matches1.empty:
            print(matches1[[home_col, away_col, res_col, 'Date']].to_string())
            print("Outcome Counts:", matches1[res_col].value_counts())
            
        # Direction 2
        mask2 = (data_v1[home_col] == away_id) & (data_v1[away_col] == home_id)
        matches2 = data_v1[mask2]
        
        print(f"\nMatches: ID {away_id} (Home) vs ID {home_id} (Away)")
        print(f"Count: {len(matches2)}")
        if not matches2.empty:
            print(matches2[[home_col, away_col, res_col, 'Date']].to_string())
            print("Outcome Counts:", matches2[res_col].value_counts())

if __name__ == "__main__":
    debug_v1_matches()
