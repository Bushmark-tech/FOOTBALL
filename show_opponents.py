"""
Show which teams Burnley and Man United played against
"""
import os
import django
import pandas as pd
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, get_column_names, load_team_mapping

# Load the data
print("Loading football data and team mapping...")
data = load_football_data(1, use_cache=False)
mapping = load_team_mapping()

# Create reverse mapping (ID -> Name)
reverse_mapping = {str(v): k for k, v in mapping.items()}

home_col, away_col, result_col = get_column_names("v1")

# Get Burnley and Man United IDs
burnley_id = str(mapping.get('Burnley', mapping.get('burnley')))
manutd_id = str(mapping.get('Man United', mapping.get('man united')))

print(f"\nBurnley ID: {burnley_id}")
print(f"Man United ID: {manutd_id}")

print(f"\n{'='*100}")
print(f"BURNLEY - Last 5 Matches (with opponent names)")
print(f"{'='*100}")

# Get Burnley matches
burnley_matches = data[
    (data[home_col].astype(str) == burnley_id) | 
    (data[away_col].astype(str) == burnley_id)
].copy()

if 'Date' in burnley_matches.columns:
    burnley_matches['Date'] = pd.to_datetime(burnley_matches['Date'], errors='coerce')
    burnley_matches = burnley_matches.sort_values('Date', ascending=False).head(5)

for idx, row in burnley_matches.iterrows():
    home_id = str(row[home_col])
    away_id = str(row[away_col])
    result = str(row[result_col])
    date = row.get('Date', 'N/A')
    
    # Get team names
    home_name = reverse_mapping.get(home_id, f"Team {home_id}")
    away_name = reverse_mapping.get(away_id, f"Team {away_id}")
    
    is_home = (home_id == burnley_id)
    
    # Decode result
    if result == '2' or result == 'H':
        result_text = "Home Win"
    elif result == '1' or result == 'D':
        result_text = "Draw"
    elif result == '0' or result == 'A':
        result_text = "Away Win"
    else:
        result_text = result
    
    # Determine Burnley's result
    if result_text == "Draw":
        burnley_result = "D"
    elif (result_text == "Home Win" and is_home) or (result_text == "Away Win" and not is_home):
        burnley_result = "W"
    else:
        burnley_result = "L"
    
    # Show opponent
    opponent = away_name if is_home else home_name
    location = "HOME" if is_home else "AWAY"
    
    print(f"{date} | {location:4} vs {opponent:20} | Result: {result_text:10} | Burnley: {burnley_result}")

print(f"\n{'='*100}")
print(f"MAN UNITED - Last 5 Matches (with opponent names)")
print(f"{'='*100}")

# Get Man United matches
manutd_matches = data[
    (data[home_col].astype(str) == manutd_id) | 
    (data[away_col].astype(str) == manutd_id)
].copy()

if 'Date' in manutd_matches.columns:
    manutd_matches['Date'] = pd.to_datetime(manutd_matches['Date'], errors='coerce')
    manutd_matches = manutd_matches.sort_values('Date', ascending=False).head(5)

for idx, row in manutd_matches.iterrows():
    home_id = str(row[home_col])
    away_id = str(row[away_col])
    result = str(row[result_col])
    date = row.get('Date', 'N/A')
    
    # Get team names
    home_name = reverse_mapping.get(home_id, f"Team {home_id}")
    away_name = reverse_mapping.get(away_id, f"Team {away_id}")
    
    is_home = (home_id == manutd_id)
    
    # Decode result
    if result == '2' or result == 'H':
        result_text = "Home Win"
    elif result == '1' or result == 'D':
        result_text = "Draw"
    elif result == '0' or result == 'A':
        result_text = "Away Win"
    else:
        result_text = result
    
    # Determine Man United's result
    if result_text == "Draw":
        manutd_result = "D"
    elif (result_text == "Home Win" and is_home) or (result_text == "Away Win" and not is_home):
        manutd_result = "W"
    else:
        manutd_result = "L"
    
    # Show opponent
    opponent = away_name if is_home else home_name
    location = "HOME" if is_home else "AWAY"
    
    print(f"{date} | {location:4} vs {opponent:20} | Result: {result_text:10} | Man Utd: {manutd_result}")

print(f"\n{'='*100}")
