"""
Check if Grasshoppers vs Young Boys exists in the datasets
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, find_team_in_data

def check_swiss_teams():
    print("\n" + "="*80)
    print("CHECKING: Grasshoppers vs Young Boys")
    print("="*80)
    
    for dataset_num in [1, 2]:
        print(f"\nDataset {dataset_num}:")
        data = load_football_data(dataset_num)
        
        if data is None or data.empty:
            print(f"  ❌ Empty or None")
            continue
        
        # Determine columns
        if 'Home' in data.columns:
            home_col, away_col = 'Home', 'Away'
        else:
            home_col, away_col = 'HomeTeam', 'AwayTeam'
        
        # Check for teams
        grass_match = find_team_in_data("Grasshoppers", data, home_col)
        yb_match = find_team_in_data("Young Boys", data, home_col)
        
        print(f"  Grasshoppers: {grass_match if grass_match else '❌ Not found'}")
        print(f"  Young Boys: {yb_match if yb_match else '❌ Not found'}")
        
        # Show sample teams from dataset
        if not grass_match and not yb_match:
            print(f"\n  Sample teams in dataset {dataset_num}:")
            unique_teams = data[home_col].unique()[:15]
            for team in unique_teams:
                print(f"    - {team}")

if __name__ == "__main__":
    check_swiss_teams()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("If Swiss teams are not in the dataset, the warnings are CORRECT.")
    print("The system is working as intended - showing fallback for missing data.")
