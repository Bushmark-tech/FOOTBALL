
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

def debug_probs_v1_smoothed():
    print("DEBUGGING PROBABILITIES WITH SMOOTHING (v1)")
    print("="*50)
    
    repo = get_repository()
    data_v1 = repo.get_dataset(1)
    
    if data_v1 is not None:
        print(f"Loaded v1 data: {len(data_v1)} rows")
        
        # We know IDs from previous debug: Burnley=70, Man City=233
        # But calculate_probabilities_model2 expects string names or values that match the dataset
        # If dataset has IDs, we must pass IDs!
        home_team = 70
        away_team = 233
        
        print(f"Testing with IDs: Home={home_team}, Away={away_team}")
        
        # Run calculation
        probs = analytics.calculate_probabilities_model2(home_team, away_team, data_v1, version="v1")
        print(f"\nCalculated Probs: {probs}")
        
        # Also test with String Names (which is what the view does)
        # IF the view passes strings, analytics.py must find the ID.
        # But analytics.py 'find_team_in_data' logic should handle it.
        # Let's test that too.
        print(f"\nTesting with Names: Home='Burnley', Away='Man City'")
        probs_names = analytics.calculate_probabilities_model2("Burnley", "Man City", data_v1, version="v1")
        print(f"Calculated Probs (Names): {probs_names}")

if __name__ == "__main__":
    debug_probs_v1_smoothed()
