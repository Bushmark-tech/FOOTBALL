import os
import django
import pandas as pd
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, get_column_names, load_team_mapping

# Load the data
print("Loading football data...")
data = load_football_data(1, use_cache=False)  # Dataset 1 for Premier League teams

print(f"\nDataset shape: {data.shape}")
print(f"Columns: {list(data.columns)}")

# Check if data uses IDs
home_col, away_col, result_col = get_column_names("v1")
print(f"\nColumn names: Home={home_col}, Away={away_col}, Result={result_col}")

# Check data type
if not data.empty:
    sample_home = data[home_col].iloc[0]
    print(f"Sample home value: {sample_home} (type: {type(sample_home)})")
    
    # Check if using IDs - properly check for numpy types
    use_ids = isinstance(sample_home, (int, float, np.integer, np.floating))
    print(f"Using IDs: {use_ids}")
    
    if use_ids:
        # Load mapping
        mapping = load_team_mapping()
        print(f"\nTeam mapping loaded: {len(mapping)} teams")
        
        # Find Burnley and Man United IDs
        burnley_id = None
        manutd_id = None
        
        for name, tid in mapping.items():
            if 'burnley' in name.lower():
                print(f"Found Burnley: {name} -> ID {tid}")
                burnley_id = str(tid)
            if 'man' in name.lower() and 'united' in name.lower():
                print(f"Found Man United: {name} -> ID {tid}")
                manutd_id = str(tid)
        
        if burnley_id and manutd_id:
            print(f"\n{'='*80}")
            print(f"BURNLEY (ID: {burnley_id}) - Last 5 Matches")
            print(f"{'='*80}")
            
            # Get Burnley matches
            burnley_matches = data[
                (data[home_col].astype(str) == burnley_id) | 
                (data[away_col].astype(str) == burnley_id)
            ].copy()
            
            if 'Date' in burnley_matches.columns:
                burnley_matches['Date'] = pd.to_datetime(burnley_matches['Date'], errors='coerce')
                burnley_matches = burnley_matches.sort_values('Date', ascending=False).head(5)
            else:
                burnley_matches = burnley_matches.tail(5)
            
            print(f"Found {len(burnley_matches)} matches\n")
            
            for idx, row in burnley_matches.iterrows():
                home = str(row[home_col])
                away = str(row[away_col])
                result = str(row[result_col])
                date = row.get('Date', 'N/A')
                
                is_home = (home == burnley_id)
                
                # Decode result
                if result == '2' or result == 'H':
                    result_text = "Home Win"
                elif result == '1' or result == 'D':
                    result_text = "Draw"
                elif result == '0' or result == 'A':
                    result_text = "Away Win"
                else:
                    result_text = result
                
                # Determine Burnley's result
                if result_text == "Draw":
                    burnley_result = "D"
                elif (result_text == "Home Win" and is_home) or (result_text == "Away Win" and not is_home):
                    burnley_result = "W"
                else:
                    burnley_result = "L"
                
                print(f"{date} | Home: {home} vs Away: {away} | Result: {result_text} | Burnley: {'HOME' if is_home else 'AWAY'} -> {burnley_result}")
            
            print(f"\n{'='*80}")
            print(f"MAN UNITED (ID: {manutd_id}) - Last 5 Matches")
            print(f"{'='*80}")
            
            # Get Man United matches
            manutd_matches = data[
                (data[home_col].astype(str) == manutd_id) | 
                (data[away_col].astype(str) == manutd_id)
            ].copy()
            
            if 'Date' in manutd_matches.columns:
                manutd_matches['Date'] = pd.to_datetime(manutd_matches['Date'], errors='coerce')
                manutd_matches = manutd_matches.sort_values('Date', ascending=False).head(5)
            else:
                manutd_matches = manutd_matches.tail(5)
            
            print(f"Found {len(manutd_matches)} matches\n")
            
            for idx, row in manutd_matches.iterrows():
                home = str(row[home_col])
                away = str(row[away_col])
                result = str(row[result_col])
                date = row.get('Date', 'N/A')
                
                is_home = (home == manutd_id)
                
                # Decode result
                if result == '2' or result == 'H':
                    result_text = "Home Win"
                elif result == '1' or result == 'D':
                    result_text = "Draw"
                elif result == '0' or result == 'A':
                    result_text = "Away Win"
                else:
                    result_text = result
                
                # Determine Man United's result
                if result_text == "Draw":
                    manutd_result = "D"
                elif (result_text == "Home Win" and is_home) or (result_text == "Away Win" and not is_home):
                    manutd_result = "W"
                else:
                    manutd_result = "L"
                
                print(f"{date} | Home: {home} vs Away: {away} | Result: {result_text} | Man United: {'HOME' if is_home else 'AWAY'} -> {manutd_result}")
    else:
        # Using team names directly - need to check data type first
        print("\nData is using team names (not IDs)")
        print("Note: This branch may not execute if data uses numeric IDs")
        
        # This code won't run if use_ids is True, so it's safe

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
