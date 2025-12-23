"""Check dataset 2 in detail for Switzerland teams."""
import pandas as pd
import os

print("=" * 70)
print("Detailed Check of Dataset 2 for Switzerland Teams")
print("=" * 70)

d2_path = 'data/football_data2.csv'

if os.path.exists(d2_path):
    try:
        # Try different encodings
        try:
            d2 = pd.read_csv(d2_path, encoding='utf-8')
        except:
            d2 = pd.read_csv(d2_path, encoding='latin-1')
        
        print(f"\nDataset 2: {len(d2)} rows")
        print(f"Columns: {list(d2.columns)}")
        
        # Find team columns
        if 'HomeTeam' in d2.columns:
            home_col, away_col = 'HomeTeam', 'AwayTeam'
        elif 'Home' in d2.columns:
            home_col, away_col = 'Home', 'Away'
        else:
            print("Cannot find team columns")
            exit(1)
        
        print(f"\nUsing columns: {home_col}, {away_col}")
        
        # Get all unique teams
        all_home_teams = set(d2[home_col].astype(str).dropna().unique())
        all_away_teams = set(d2[away_col].astype(str).dropna().unique())
        all_teams = sorted(all_home_teams | all_away_teams)
        
        print(f"\nTotal unique teams: {len(all_teams)}")
        print(f"\nAll teams in dataset 2:")
        for i, team in enumerate(all_teams, 1):
            print(f"  {i}. {team}")
        
        # Check for Switzerland-related terms
        print(f"\n{'='*70}")
        print("Searching for Switzerland-related teams:")
        swiss_keywords = ['swiss', 'basel', 'zurich', 'lausanne', 'grasshopper', 'young', 'lugano', 'luzern', 'servette', 'sion', 'gallen', 'winterthur', 'yverdon']
        
        swiss_teams_found = []
        for team in all_teams:
            team_lower = str(team).lower()
            for keyword in swiss_keywords:
                if keyword in team_lower:
                    swiss_teams_found.append(team)
                    break
        
        if swiss_teams_found:
            print(f"\n✅ Found {len(swiss_teams_found)} Switzerland-related teams:")
            for team in swiss_teams_found:
                home_count = len(d2[d2[home_col].astype(str).str.contains(team, case=False, na=False)])
                away_count = len(d2[d2[away_col].astype(str).str.contains(team, case=False, na=False)])
                print(f"   {team}: {home_count} home matches, {away_count} away matches")
        else:
            print("\n❌ No Switzerland teams found")
        
        # Show sample rows
        print(f"\n{'='*70}")
        print("Sample rows from dataset 2:")
        print(d2[[home_col, away_col]].head(20).to_string())
        
        # Check if there's a League column that might indicate Switzerland
        if 'League' in d2.columns:
            print(f"\n{'='*70}")
            print("Leagues in dataset 2:")
            leagues = d2['League'].unique() if 'League' in d2.columns else []
            for league in leagues:
                print(f"   {league}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Dataset 2 not found at {d2_path}")

print("\n" + "=" * 70)







