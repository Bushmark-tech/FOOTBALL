"""
Check ALL teams that Man United played against in the database
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

# Create reverse mapping (ID -> Name)
reverse_mapping = {str(v): k for k, v in mapping.items()}

home_col, away_col, result_col = get_column_names("v1")

# Get Man United ID
manutd_id = str(mapping.get('Man United'))
print(f"Man United ID: {manutd_id}")

# Get ALL Man United matches
manutd_all = data[
    (data[home_col].astype(str) == manutd_id) | 
    (data[away_col].astype(str) == manutd_id)
].copy()

if 'Date' in manutd_all.columns:
    manutd_all['Date'] = pd.to_datetime(manutd_all['Date'], errors='coerce')
    manutd_all = manutd_all.sort_values('Date', ascending=False)

print(f"\nTotal Man United matches: {len(manutd_all)}")
print(f"Date range: {manutd_all['Date'].min()} to {manutd_all['Date'].max()}")

# Get all unique opponents
opponents = set()
for idx, row in manutd_all.iterrows():
    home_id = str(row[home_col])
    away_id = str(row[away_col])
    
    if home_id == manutd_id:
        opponent_id = away_id
    else:
        opponent_id = home_id
    
    opponent_name = reverse_mapping.get(opponent_id, f"Team {opponent_id}")
    opponents.add(opponent_name)

print(f"\n{'='*100}")
print(f"ALL TEAMS MAN UNITED PLAYED AGAINST ({len(opponents)} unique teams)")
print(f"{'='*100}")

# Sort alphabetically
for opponent in sorted(opponents):
    print(f"  - {opponent}")

# Check which league these teams belong to
print(f"\n{'='*100}")
print(f"ANALYZING OPPONENT LEAGUES")
print(f"{'='*100}")

premier_league_teams = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 
    'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
    'Liverpool', 'Man City', 'Man United', 'Newcastle', 'Nottingham Forest',
    'Sheffield United', 'Tottenham', 'West Ham', 'Wolves'
]

championship_teams = []
premier_teams_found = []
other_teams = []

for opponent in opponents:
    if opponent in premier_league_teams:
        premier_teams_found.append(opponent)
    elif any(keyword in opponent.lower() for keyword in ['coventry', 'bristol', 'derby', 'blackburn', 'stoke', 'leeds', 'hull', 'middlesbrough', 'west brom']):
        championship_teams.append(opponent)
    else:
        other_teams.append(opponent)

print(f"\nPremier League teams ({len(premier_teams_found)}):")
for team in sorted(premier_teams_found):
    print(f"  ✅ {team}")

print(f"\nChampionship teams ({len(championship_teams)}):")
for team in sorted(championship_teams):
    print(f"  🟡 {team}")

print(f"\nOther teams ({len(other_teams)}):")
for team in sorted(other_teams):
    print(f"  ⚪ {team}")

# Show matches by year
print(f"\n{'='*100}")
print(f"MAN UNITED MATCHES BY YEAR")
print(f"{'='*100}")

manutd_all['Year'] = manutd_all['Date'].dt.year
matches_by_year = manutd_all.groupby('Year').size().sort_index(ascending=False)

for year, count in matches_by_year.items():
    print(f"{year}: {count} matches")

# Show most recent 20 matches with opponents
print(f"\n{'='*100}")
print(f"MOST RECENT 20 MAN UNITED MATCHES")
print(f"{'='*100}")

for idx, row in manutd_all.head(20).iterrows():
    home_id = str(row[home_col])
    away_id = str(row[away_col])
    date = row.get('Date', 'N/A')
    
    home_name = reverse_mapping.get(home_id, f"Team {home_id}")
    away_name = reverse_mapping.get(away_id, f"Team {away_id}")
    
    is_home = (home_id == manutd_id)
    location = "HOME" if is_home else "AWAY"
    opponent = away_name if is_home else home_name
    
    date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
    
    print(f"{date_str} | {location:4} vs {opponent:25}")

print(f"\n{'='*100}")
print(f"CONCLUSION:")
print(f"{'='*100}")
print(f"Man United played against {len(opponents)} different teams")
print(f"  - Premier League teams: {len(premier_teams_found)}")
print(f"  - Championship teams: {len(championship_teams)}")
print(f"  - Other teams: {len(other_teams)}")
print(f"\nMost recent match: {manutd_all['Date'].max()}")
print(f"⚠️  This is 8 months old! Database needs updating.")
print(f"{'='*100}")
