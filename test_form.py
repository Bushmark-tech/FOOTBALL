"""Test script to verify team form calculation."""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import get_team_recent_form_original, load_football_data
from predictor.models import League, Team

def test_team_form():
    """Test team form calculation for Grasshoppers and Lausanne."""
    print("=" * 70)
    print("Testing Team Form Calculation")
    print("=" * 70)
    
    home_team = "Grasshoppers"
    away_team = "Lausanne"
    
    # Check which category these teams belong to
    try:
        swiss_league = League.objects.filter(name__icontains="Switzerland").first()
        if swiss_league:
            print(f"\nSwitzerland League found: {swiss_league.name}, Category: {swiss_league.category}")
            teams = Team.objects.filter(league=swiss_league)
            print(f"Teams in league: {[t.name for t in teams]}")
    except Exception as e:
        print(f"Error checking league: {e}")
    
    # Load dataset 2 (for Others category teams)
    print("\nLoading dataset 2 (for Switzerland League teams)...")
    data = load_football_data(2, use_cache=True)
    
    data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
    
    if data_empty:
        print("⚠️  Dataset 2 is empty!")
        return
    
    print(f"Dataset 2 loaded: {len(data)} rows")
    
    # Check if teams exist in the data
    if hasattr(data, 'columns'):
        home_col = "HomeTeam" if "HomeTeam" in data.columns else "Home"
        away_col = "AwayTeam" if "AwayTeam" in data.columns else "Away"
        
        print(f"\nChecking for {home_team} in dataset...")
        home_matches = data[data[home_col].astype(str).str.contains(home_team, case=False, na=False)]
        away_matches = data[data[away_col].astype(str).str.contains(home_team, case=False, na=False)]
        print(f"  Found {len(home_matches)} matches as home team")
        print(f"  Found {len(away_matches)} matches as away team")
        
        print(f"\nChecking for {away_team} in dataset...")
        home_matches2 = data[data[home_col].astype(str).str.contains(away_team, case=False, na=False)]
        away_matches2 = data[data[away_col].astype(str).str.contains(away_team, case=False, na=False)]
        print(f"  Found {len(home_matches2)} matches as home team")
        print(f"  Found {len(away_matches2)} matches as away team")
        
        # Show unique team names that contain these strings
        all_home_teams = set(data[home_col].astype(str).unique())
        all_away_teams = set(data[away_col].astype(str).unique())
        all_teams = sorted(all_home_teams | all_away_teams)
        
        grasshoppers_variants = [t for t in all_teams if 'grass' in t.lower()]
        lausanne_variants = [t for t in all_teams if 'laus' in t.lower()]
        
        print(f"\nTeam name variants found:")
        print(f"  Grasshoppers variants: {grasshoppers_variants[:10]}")
        print(f"  Lausanne variants: {lausanne_variants[:10]}")
    
    # Calculate form
    print(f"\nCalculating form for {home_team}...")
    home_form = get_team_recent_form_original(home_team, data, version="v1")
    print(f"  Form: {home_form}")
    print(f"  Expected: WLDWL")
    
    print(f"\nCalculating form for {away_team}...")
    away_form = get_team_recent_form_original(away_team, data, version="v1")
    print(f"  Form: {away_form}")
    print(f"  Expected: LLWWW")
    
    print("\n" + "=" * 70)
    if home_form == "WLDWL" and away_form == "LLWWW":
        print("✅ Forms match expected values!")
    else:
        print("❌ Forms do NOT match expected values!")
        print(f"   Expected: Grasshoppers=WLDWL, Lausanne=LLWWW")
        print(f"   Got:      Grasshoppers={home_form}, Lausanne={away_form}")
    print("=" * 70)

if __name__ == "__main__":
    test_team_form()

