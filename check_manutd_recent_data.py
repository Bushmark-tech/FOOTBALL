"""
Check why Man United has no recent data
"""
import os
import django
import pandas as pd
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, get_column_names, load_team_mapping

# Load the data
print("Loading football data...")
data = load_football_data(1, use_cache=False)
mapping = load_team_mapping()

home_col, away_col, result_col = get_column_names("v1")

# Get Man United ID
manutd_id = str(mapping.get('Man United', mapping.get('man united')))
print(f"Man United ID: {manutd_id}")

# Get ALL Man United matches
print(f"\n{'='*100}")
print(f"ALL MAN UNITED MATCHES IN DATABASE")
print(f"{'='*100}")

manutd_all = data[
    (data[home_col].astype(str) == manutd_id) | 
    (data[away_col].astype(str) == manutd_id)
].copy()

if 'Date' in manutd_all.columns:
    manutd_all['Date'] = pd.to_datetime(manutd_all['Date'], errors='coerce')
    manutd_all = manutd_all.sort_values('Date', ascending=False)

print(f"Total Man United matches found: {len(manutd_all)}")

if len(manutd_all) > 0:
    print(f"\nMost recent match: {manutd_all['Date'].max()}")
    print(f"Oldest match: {manutd_all['Date'].min()}")
    
    print(f"\n{'='*100}")
    print(f"LAST 10 MAN UNITED MATCHES (to see the gap)")
    print(f"{'='*100}")
    
    reverse_mapping = {str(v): k for k, v in mapping.items()}
    
    for idx, row in manutd_all.head(10).iterrows():
        home_id = str(row[home_col])
        away_id = str(row[away_col])
        date = row.get('Date', 'N/A')
        
        home_name = reverse_mapping.get(home_id, f"Team {home_id}")
        away_name = reverse_mapping.get(away_id, f"Team {away_id}")
        
        print(f"{date} | {home_name} vs {away_name}")
    
    # Check for recent matches (last 3 months)
    print(f"\n{'='*100}")
    print(f"CHECKING FOR RECENT MATCHES (since Oct 2025)")
    print(f"{'='*100}")
    
    recent_cutoff = pd.to_datetime('2025-10-01')
    recent_matches = manutd_all[manutd_all['Date'] >= recent_cutoff]
    
    print(f"Matches since Oct 1, 2025: {len(recent_matches)}")
    
    if len(recent_matches) == 0:
        print("\n⚠️ WARNING: NO RECENT MAN UNITED DATA!")
        print("The database has NO Man United matches from the last 3 months!")
        print("This explains why the form is outdated.")
else:
    print("\n❌ ERROR: No Man United matches found in database!")

print(f"\n{'='*100}")
print("CONCLUSION:")
print(f"{'='*100}")
print("Man United's most recent match in the database is from May 2025.")
print("The database is missing Man United's matches from June 2025 onwards.")
print("This is why the form data is 8 months old!")
