
import pandas as pd
import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data

# Load data directly
df = pd.read_csv('data/football_data1.csv')

# ID for Man United is now 234
man_utd_id = 234
burnley_id = 70

print(f"Checking data for Man United (ID: {man_utd_id})")
# Filter for Man United matches
man_utd_matches = df[(df['HomeTeam'] == man_utd_id) | (df['AwayTeam'] == man_utd_id)].copy()
if not man_utd_matches.empty:
    man_utd_matches['Date'] = pd.to_datetime(man_utd_matches['Date'])
    last_5_man = man_utd_matches.sort_values('Date').tail(5)
    
    print("\nLast 5 matches for Man United (234):")
    for idx, row in last_5_man.iterrows():
        is_home = (row['HomeTeam'] == man_utd_id)
        result = row['FTR'] # 0=AwayWin, 1=Draw, 2=HomeWin
        
        # Determine W/D/L
        outcome = "?"
        if result == 1:
            outcome = "D"
        elif (is_home and result == 2) or (not is_home and result == 0):
            outcome = "W"
        else:
            outcome = "L"
            
        print(f"Date: {row['Date'].date()} | Vs: {row['AwayTeam'] if is_home else row['HomeTeam']} | Res: {result} | Form: {outcome}")
else:
    print("No matches found for ID 234")

print(f"\nChecking data for Burnley (ID: {burnley_id})")
burnley_matches = df[(df['HomeTeam'] == burnley_id) | (df['AwayTeam'] == burnley_id)].copy()
if not burnley_matches.empty:
    burnley_matches['Date'] = pd.to_datetime(burnley_matches['Date'])
    last_5_burn = burnley_matches.sort_values('Date').tail(5)
    
    print("\nLast 5 matches for Burnley (70):")
    for idx, row in last_5_burn.iterrows():
        is_home = (row['HomeTeam'] == burnley_id)
        result = row['FTR']
        
        outcome = "?"
        if result == 1:
            outcome = "D"
        elif (is_home and result == 2) or (not is_home and result == 0):
            outcome = "W"
        else:
            outcome = "L"
            
        print(f"Date: {row['Date'].date()} | Vs: {row['AwayTeam'] if is_home else row['HomeTeam']} | Res: {result} | Form: {outcome}")
