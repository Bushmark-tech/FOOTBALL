
import os
import sys
import django
import pandas as pd
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.strategies import HistoricalH2HCalculator
from predictor.repositories import get_repository
from predictor.adapters import DataAdapterFactory

def debug_strategies():
    print("DEBUGGING STRATEGIES (HistoricalH2HCalculator)")
    print("="*50)
    
    repo = get_repository()
    data_v1 = repo.get_dataset(1)
    
    if data_v1 is not None:
        adapter = DataAdapterFactory.create(data_v1, "v1")
        
        # ID 70 vs 233
        home_team = 70
        away_team = 233
        
        calc = HistoricalH2HCalculator()
        print(f"Calculating for Home={home_team}, Away={away_team} using Strategy...")
        
        result = calc.calculate(home_team, away_team, data_v1, adapter)
        print(f"\nStrategy Result: {result}")
        
        # Names
        # Note: Strategy expects IDs if data uses IDs. 
        # The main app flow matches names to IDs before calling strategy.
        # But let's verify if Strategy handles names if passed?
        # No, strategy just uses repo.get_h2h_matches which does string conversion.
        # But repo checks AGAINST data. If data has IDs, we must pass IDs (as strings or ints).
        # We verified passing "Burnley" (string) to repo works ONLY if "Burnley" is in the data.
        # But "Burnley" is NOT in v1 data. IDs are.
        # So Main App MUST resolve "Burnley" -> 70 before calling Strategy.
        # In analytics.py advanced_predict_match:
        # exact_home = find_team_in_data(...)
        # if exact_home is not None: home_team = exact_home
        # This converts "Burnley" -> 70.
        # So Strategy receives 70.
        
        # So my test above (passing 70, 233) mimics the App correctly.

if __name__ == "__main__":
    debug_strategies()
