
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

def debug_data_content():
    print("DEBUGGING DATA CONTENT")
    print("="*50)
    
    repo = get_repository()
    
    # Check Dataset 2
    print("\n--- Checking Dataset 2 (v2) ---")
    data_v2 = repo.get_dataset(2)
    if data_v2 is not None:
        adapter = DataAdapterFactory.create(data_v2, "v2")
        home = adapter.get_home_column()
        away = adapter.get_away_column()
        
        print(f"Sample Rows:\n{data_v2[[home, away]].head(5).to_string()}")
        
        unique = pd.concat([data_v2[home], data_v2[away]]).unique()
        print(f"\nFirst 20 Unique Teams (v2): {unique[:20]}")
        
        # Check types
        print(f"Team column type: {data_v2[home].dtype}")
    
    # Check Dataset 1
    print("\n--- Checking Dataset 1 (v1) ---")
    data_v1 = repo.get_dataset(1)
    if data_v1 is not None:
        adapter = DataAdapterFactory.create(data_v1, "v1")
        home = adapter.get_home_column()
        away = adapter.get_away_column()
        
        print(f"Sample Rows:\n{data_v1[[home, away]].head(5).to_string()}")
        
        unique = pd.concat([data_v1[home], data_v1[away]]).unique()
        print(f"\nFirst 20 Unique Teams (v1): {unique[:20]}")

if __name__ == "__main__":
    debug_data_content()
