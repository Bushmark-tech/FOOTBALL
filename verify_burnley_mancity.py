
import pandas as pd
import os
import sys

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'football_data1.csv')

print(f"Loading data from {DATA_FILE}...")
df = pd.read_csv(DATA_FILE, encoding='latin-1', low_memory=False)

# IDs from team_mapping.csv
# Burnley: 70
# Man City: 233
home_id = "70"
away_id = "233"

# Ensure HomeTeam/AwayTeam are strings for comparison
df['HomeTeam'] = df['HomeTeam'].astype(str)
df['AwayTeam'] = df['AwayTeam'].astype(str)

print(f"Searching for Home ID: {home_id}")
print(f"Searching for Away ID: {away_id}")

# 1. H2H Analysis
print("\n--- Head to Head (Last 10) ---")
mask = ((df['HomeTeam'] == home_id) & (df['AwayTeam'] == away_id)) | \
       ((df['HomeTeam'] == away_id) & (df['AwayTeam'] == home_id))

h2h = df[mask].sort_values('Date', ascending=False)
print(f"Total H2H Matches found: {len(h2h)}")
columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG']
# Only use existing columns
existing_cols = [c for c in columns if c in df.columns]
print(h2h[existing_cols].head(10).to_string())

# Calculate Probabilities
burnley_wins = 0
man_city_wins = 0
draws = 0

for _, row in h2h.iterrows():
    result = str(row['FTR'])
    # Map numeric result if needed
    if result == '0': result = 'A'
    elif result == '1': result = 'D'
    elif result == '2': result = 'H'
    
    if result == 'D':
        draws += 1
    elif row['HomeTeam'] == home_id:
        if result == 'H': burnley_wins += 1
        else: man_city_wins += 1
    else: # HomeTeam == away_id (Man City)
        if result == 'H': man_city_wins += 1
        else: burnley_wins += 1

total = len(h2h)
if total > 0:
    print(f"\nWin Counts: Burnley: {burnley_wins}, Draw: {draws}, Man City: {man_city_wins}")
    print(f"Probabilities: Burnley: {burnley_wins/total:.2%}, Draw: {draws/total:.2%}, Man City: {man_city_wins/total:.2%}")

# 2. Recent Form
def get_form(team_id, team_name):
    print(f"\n--- Recent Form: {team_name} (ID: {team_id}) ---")
    mask = (df['HomeTeam'] == team_id) | (df['AwayTeam'] == team_id)
    matches = df[mask].sort_values('Date', ascending=False).head(5)
    existing_cols = [c for c in columns if c in df.columns]
    print(matches[existing_cols].to_string())
    
    form_str = ""
    for _, row in matches.iterrows():
        result = str(row['FTR'])
        if result == '0': result = 'A'
        elif result == '1': result = 'D'
        elif result == '2': result = 'H'
        
        if result == 'D':
            form_str += "D"
        elif (row['HomeTeam'] == team_id and result == 'H') or (row['AwayTeam'] == team_id and result == 'A'):
            form_str += "W"
        else:
            form_str += "L"
    print(f"Form String: {form_str}")

get_form(home_id, "Burnley")
get_form(away_id, "Man City")
