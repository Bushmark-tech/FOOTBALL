
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

def debug_ids():
    repo = get_repository()
    
    print("\n--- Checking Dataset 1 (ID check) ---")
    data_v1 = repo.get_dataset(1)
    if data_v1 is not None:
        adapter = DataAdapterFactory.create(data_v1, "v1")
        home = adapter.get_home_column()
        away = adapter.get_away_column()
        
        unique_ids = pd.concat([data_v1[home], data_v1[away]]).unique()
        print(f"Total Unique IDs in v1: {len(unique_ids)}")
        
        # Check specific IDs
        check_ids = [70, 233] # Burnley, Man City
        for tid in check_ids:
            if tid in unique_ids:
                print(f"ID {tid} FOUND in v1")
            else:
                print(f"ID {tid} NOT FOUND in v1")
                
        # List all IDs to see range
        print(f"Sample IDs: {sorted(unique_ids)[:20]}")
        
    print("\n--- Checking Dataset 2 (Name check) ---")
    data_v2 = repo.get_dataset(2)
    if data_v2 is not None:
        adapter = DataAdapterFactory.create(data_v2, "v2")
        home = adapter.get_home_column()
        away = adapter.get_away_column()
        
        unique_names = pd.concat([data_v2[home].dropna(), data_v2[away].dropna()]).unique()
        unique_names = sorted([str(n) for n in unique_names])
        
        print("\nSearching for City/Man/Burn in v2:")
        for name in unique_names:
            if 'man' in name.lower() or 'city' in name.lower() or 'burn' in name.lower():
                print(f" - {name}")

if __name__ == "__main__":
    debug_ids()
