"""Test Switzerland teams with real data from lGIC dataset 2."""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import (
    calculate_probabilities_original, 
    get_team_recent_form_original,
    load_football_data
)

print("=" * 70)
print("Testing Switzerland Teams with Real Data")
print("=" * 70)

# Load dataset 2 (should now use lGIC folder)
data = load_football_data(2, use_cache=False)  # Don't use cache to get fresh data

print(f"\nDataset 2 loaded: {len(data)} rows")
print(f"Columns: {list(data.columns)[:10]}")

# Detect version
if 'Home' in data.columns:
    version = "v2"
    print(f"Detected version: v2 (Home/Away/Res)")
else:
    version = "v1"
    print(f"Detected version: v1 (HomeTeam/AwayTeam/FTR)")

# Test teams
test_teams = ["Grasshoppers", "Lausanne", "Basel", "Zurich"]

for team in test_teams:
    print(f"\n{'='*70}")
    print(f"Team: {team}")
    print(f"{'='*70}")
    
    # Get form
    form = get_team_recent_form_original(team, data, version=version)
    print(f"Form: {form}")
    
    # Check if it's from real data or manual/hash
    if team == "Grasshoppers" and form == "WLDWL":
        print("  ⚠️  Using manual form (not from data)")
    elif team == "Lausanne" and form == "LLWWW":
        print("  ⚠️  Using manual form (not from data)")
    else:
        print("  ✅ Form from real data")

# Test historical probabilities
print(f"\n{'='*70}")
print("Historical Probabilities Test")
print(f"{'='*70}")

home_team = "Grasshoppers"
away_team = "Lausanne"

probs = calculate_probabilities_original(home_team, away_team, data, version=version)
print(f"\n{home_team} vs {away_team}:")
if probs:
    print(f"  Home Win: {probs.get('Home Team Win', 0):.1f}%")
    print(f"  Draw:     {probs.get('Draw', 0):.1f}%")
    print(f"  Away Win: {probs.get('Away Team Win', 0):.1f}%")
    
    # Check if it's from H2H data or form-based
    total = sum(probs.values())
    if abs(total - 100.0) < 0.1:
        print(f"  ✅ Probabilities normalized")
    else:
        print(f"  ⚠️  Probabilities don't sum to 100%")
else:
    print("  ❌ No probabilities returned")

# Check H2H data directly
print(f"\n{'='*70}")
print("Head-to-Head Data Check")
print(f"{'='*70}")

if version == "v2":
    home_col, away_col, result_col = "Home", "Away", "Res"
else:
    home_col, away_col, result_col = "HomeTeam", "AwayTeam", "FTR"

h2h = data[
    (data[home_col].astype(str).str.strip() == home_team) &
    (data[away_col].astype(str).str.strip() == away_team)
]

print(f"\nH2H matches found: {len(h2h)}")
if len(h2h) > 0:
    print("  ✅ Using real H2H data for probabilities")
    print(f"\n  Recent H2H matches (last 5):")
    h2h_sorted = h2h.sort_values('Date', ascending=False).head(5) if 'Date' in h2h.columns else h2h.head(5)
    for idx, row in h2h_sorted.iterrows():
        date = row.get('Date', 'N/A')
        result = row[result_col]
        print(f"    {date}: {home_team} vs {away_team} = {result}")
else:
    print("  ⚠️  No H2H data - using form-based probabilities")

print("\n" + "=" * 70)







