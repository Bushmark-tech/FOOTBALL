"""Check lGIC folder's dataset 2 for Switzerland teams."""
import pandas as pd
import os
import sys

print("=" * 70)
print("Checking lGIC Dataset 2 for Switzerland Teams")
print("=" * 70)

# Check lGIC folder
lgic_path = os.path.join('..', 'lGIC', 'football_data2.csv')
if not os.path.exists(lgic_path):
    lgic_path = os.path.join('lGIC', 'football_data2.csv')

if os.path.exists(lgic_path):
    try:
        d2 = pd.read_csv(lgic_path, encoding='latin-1')
        print(f"\nDataset 2: {len(d2)} rows")
        print(f"Columns: {list(d2.columns)}")
        
        # Find team columns
        if 'HomeTeam' in d2.columns:
            home_col, away_col = 'HomeTeam', 'AwayTeam'
        elif 'Home' in d2.columns:
            home_col, away_col = 'Home', 'Away'
        else:
            print("Cannot find team columns")
            print("Available columns:", list(d2.columns))
            exit(1)
        
        print(f"\nUsing columns: {home_col}, {away_col}")
        
        # Get all unique teams
        all_home_teams = set(d2[home_col].astype(str).dropna().unique())
        all_away_teams = set(d2[away_col].astype(str).dropna().unique())
        all_teams = sorted(all_home_teams | all_away_teams)
        
        print(f"\nTotal unique teams: {len(all_teams)}")
        
        # Check for Switzerland teams
        swiss_teams = ['Basel', 'Grasshoppers', 'Lausanne', 'Lugano', 'Luzern', 
                      'Servette', 'Sion', 'St. Gallen', 'Winterthur', 'Young Boys', 
                      'Yverdon', 'Zurich']
        
        print(f"\n{'='*70}")
        print("Searching for Switzerland teams:")
        swiss_found = {}
        for team in swiss_teams:
            # Try exact match
            home_matches = d2[d2[home_col].astype(str).str.strip() == team]
            away_matches = d2[d2[away_col].astype(str).str.strip() == team]
            total = len(home_matches) + len(away_matches)
            
            # Try case-insensitive
            if total == 0:
                home_matches = d2[d2[home_col].astype(str).str.strip().str.lower() == team.lower()]
                away_matches = d2[d2[away_col].astype(str).str.strip().str.lower() == team.lower()]
                total = len(home_matches) + len(away_matches)
            
            # Try contains
            if total == 0:
                home_matches = d2[d2[home_col].astype(str).str.contains(team, case=False, na=False)]
                away_matches = d2[d2[away_col].astype(str).str.contains(team, case=False, na=False)]
                total = len(home_matches) + len(away_matches)
            
            if total > 0:
                swiss_found[team] = {
                    'home': len(home_matches),
                    'away': len(away_matches),
                    'total': total
                }
                # Show actual team name in data
                if len(home_matches) > 0:
                    actual_name = home_matches[home_col].iloc[0]
                    print(f"  {team}: {total} matches (found as '{actual_name}')")
                elif len(away_matches) > 0:
                    actual_name = away_matches[away_col].iloc[0]
                    print(f"  {team}: {total} matches (found as '{actual_name}')")
        
        if swiss_found:
            print(f"\n{'='*70}")
            print(f"Found {len(swiss_found)} Switzerland teams!")
            print(f"{'='*70}")
            
            # Show sample matches
            print("\nSample matches with Switzerland teams:")
            for team in list(swiss_found.keys())[:3]:
                matches = d2[
                    (d2[home_col].astype(str).str.contains(team, case=False, na=False)) |
                    (d2[away_col].astype(str).str.contains(team, case=False, na=False))
                ]
                if len(matches) > 0:
                    print(f"\n{team} matches (first 5):")
                    print(matches[[home_col, away_col, 'FTR' if 'FTR' in matches.columns else 'Res']].head().to_string())
        else:
            print("\nNo Switzerland teams found in dataset 2")
            print("\nSample teams in dataset 2:")
            print(list(all_teams)[:30])
        
        # Check League column if exists
        if 'League' in d2.columns:
            print(f"\n{'='*70}")
            print("Leagues in dataset 2:")
            leagues = d2['League'].value_counts()
            print(leagues.head(20))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"lGIC dataset 2 not found at {lgic_path}")
    print("Checking Football-main/data/football_data2.csv...")
    main_path = 'data/football_data2.csv'
    if os.path.exists(main_path):
        d2 = pd.read_csv(main_path, encoding='latin-1')
        print(f"Found: {len(d2)} rows")
        print(f"Teams: {list(d2['HomeTeam'].unique()) if 'HomeTeam' in d2.columns else 'N/A'}")

print("\n" + "=" * 70)







