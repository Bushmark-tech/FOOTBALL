import pandas as pd

# Check football_data1.csv
df1 = pd.read_csv('data/football_data1.csv')
print("=" * 70)
print("FOOTBALL_DATA1.CSV ANALYSIS")
print("=" * 70)
print(f"\nTotal rows: {len(df1)}")
print(f"Columns: {list(df1.columns)[:15]}")

# Check team columns
if 'HomeTeam' in df1.columns:
    print(f"\nHomeTeam data type: {df1['HomeTeam'].dtype}")
    print(f"Sample HomeTeam values:")
    print(df1['HomeTeam'].head(20).tolist())
    
    # Search for Premier League teams
    arsenal = df1[(df1['HomeTeam'] == 'Arsenal') | (df1['AwayTeam'] == 'Arsenal')]
    liverpool = df1[(df1['HomeTeam'] == 'Liverpool') | (df1['AwayTeam'] == 'Liverpool')]
    man_city = df1[(df1['HomeTeam'] == 'Man City') | (df1['AwayTeam'] == 'Man City')]
    leeds = df1[(df1['HomeTeam'] == 'Leeds') | (df1['AwayTeam'] == 'Leeds')]
    
    print(f"\n\nPremier League Teams Found:")
    print(f"Arsenal matches: {len(arsenal)}")
    print(f"Liverpool matches: {len(liverpool)}")
    print(f"Man City matches: {len(man_city)}")
    print(f"Leeds matches: {len(leeds)}")
    
    # Get all unique teams
    all_teams = sorted(set(list(df1['HomeTeam'].unique()) + list(df1['AwayTeam'].unique())))
    print(f"\n\nTotal unique teams: {len(all_teams)}")
    print(f"\nFirst 30 teams:")
    for team in all_teams[:30]:
        print(f"  - {team}")
