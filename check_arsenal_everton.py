"""
Quick diagnostic script to check if Arsenal vs Everton exists in the datasets
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, find_team_in_data, get_column_names

def check_teams_in_dataset(home, away, dataset_num):
    """Check if teams exist and have H2H data in a dataset"""
    print(f"\n{'='*80}")
    print(f"CHECKING DATASET {dataset_num}: {home} vs {away}")
    print(f"{'='*80}")
    
    data = load_football_data(dataset_num)
    
    if data is None or data.empty:
        print(f"❌ Dataset {dataset_num} is empty or None")
        return False
    
    print(f"✓ Dataset {dataset_num} loaded: {len(data)} rows")
    
    # Determine version
    if 'Home' in data.columns:
        version = "v2"
        home_col, away_col, result_col = 'Home', 'Away', 'Res'
    else:
        version = "v1"
        home_col, away_col, result_col = 'HomeTeam', 'AwayTeam', 'FTR'
    
    print(f"✓ Version: {version}, Columns: {home_col}, {away_col}, {result_col}")
    
    # Find teams using our matching function
    home_matched = find_team_in_data(home, data, home_col)
    away_matched = find_team_in_data(away, data, away_col)
    
    print(f"\nTeam Matching:")
    print(f"  '{home}' -> '{home_matched}' {'✓' if home_matched else '❌'}")
    print(f"  '{away}' -> '{away_matched}' {'✓' if away_matched else '❌'}")
    
    if not home_matched or not away_matched:
        print(f"\n❌ Teams not found in dataset {dataset_num}")
        # Show sample teams
        print(f"\nSample teams in {home_col}:")
        print(data[home_col].unique()[:10])
        return False
    
    # Check H2H data
    h2h = data[(data[home_col].astype(str).str.strip() == home_matched) & 
               (data[away_col].astype(str).str.strip() == away_matched)]
    
    print(f"\nH2H Data:")
    print(f"  Direct matches ({home_matched} home): {len(h2h)}")
    
    # Check reverse
    h2h_reverse = data[(data[home_col].astype(str).str.strip() == away_matched) & 
                       (data[away_col].astype(str).str.strip() == home_matched)]
    print(f"  Reverse matches ({away_matched} home): {len(h2h_reverse)}")
    print(f"  Total H2H matches: {len(h2h) + len(h2h_reverse)}")
    
    if len(h2h) > 0 or len(h2h_reverse) > 0:
        print(f"\n✓ H2H DATA FOUND in dataset {dataset_num}!")
        if len(h2h) > 0:
            print(f"\nSample matches ({home_matched} home):")
            for idx, row in h2h.head(3).iterrows():
                date = row.get('Date', 'N/A')
                result = row.get(result_col, 'N/A')
                print(f"  {date}: {home_matched} vs {away_matched} - Result: {result}")
        return True
    else:
        print(f"\n❌ NO H2H DATA in dataset {dataset_num}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ARSENAL VS EVERTON - DATASET DIAGNOSTIC")
    print("="*80)
    
    # Check both datasets
    found_in_1 = check_teams_in_dataset("Arsenal", "Everton", 1)
    found_in_2 = check_teams_in_dataset("Arsenal", "Everton", 2)
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Dataset 1: {'✓ H2H DATA FOUND' if found_in_1 else '❌ No H2H data'}")
    print(f"Dataset 2: {'✓ H2H DATA FOUND' if found_in_2 else '❌ No H2H data'}")
    
    if not found_in_1 and not found_in_2:
        print(f"\n⚠️ WARNING: Arsenal vs Everton not found in either dataset!")
        print(f"This is unexpected for a major Premier League fixture.")
        print(f"\nPossible reasons:")
        print(f"1. Team names in dataset are different (e.g., 'Arsenal FC')")
        print(f"2. Datasets don't include this fixture")
        print(f"3. Data loading issue")
    else:
        print(f"\n✓ Data exists! The issue is in how views.py is loading/displaying it.")
