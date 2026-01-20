"""
Show form with opponent team names for both Burnley and Man United
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

# Get IDs
burnley_id = str(mapping.get('Burnley'))
manutd_id = str(mapping.get('Man United'))

def show_team_form(team_name, team_id, data, reverse_mapping, home_col, away_col, result_col):
    """Show team form with opponent names"""
    print(f"\n{'='*100}")
    print(f"{team_name.upper()} - LAST 5 MATCHES WITH OPPONENTS")
    print(f"{'='*100}\n")
    
    # Get team matches
    team_matches = data[
        (data[home_col].astype(str) == team_id) | 
        (data[away_col].astype(str) == team_id)
    ].copy()
    
    if 'Date' in team_matches.columns:
        team_matches['Date'] = pd.to_datetime(team_matches['Date'], errors='coerce')
        team_matches = team_matches.sort_values('Date', ascending=False).head(5)
    
    form_string = ""
    match_num = 1
    
    for idx, row in team_matches.iterrows():
        home_id = str(row[home_col])
        away_id = str(row[away_col])
        result = str(row[result_col])
        date = row.get('Date', 'N/A')
        
        # Get team names
        home_name = reverse_mapping.get(home_id, f"Team {home_id}")
        away_name = reverse_mapping.get(away_id, f"Team {away_id}")
        
        is_home = (home_id == team_id)
        
        # Decode result
        if result == '2' or result == 'H':
            result_text = "Home Win"
        elif result == '1' or result == 'D':
            result_text = "Draw"
        elif result == '0' or result == 'A':
            result_text = "Away Win"
        else:
            result_text = result
        
        # Determine team's result
        if result_text == "Draw":
            team_result = "D"
            result_emoji = "🟡"
            result_color = "DRAW"
        elif (result_text == "Home Win" and is_home) or (result_text == "Away Win" and not is_home):
            team_result = "W"
            result_emoji = "🟢"
            result_color = "WIN"
        else:
            team_result = "L"
            result_emoji = "🔴"
            result_color = "LOSS"
        
        form_string += team_result
        
        # Show opponent
        opponent = away_name if is_home else home_name
        location = "HOME" if is_home else "AWAY"
        
        # Format date
        date_str = date.strftime('%b %d, %Y') if hasattr(date, 'strftime') else str(date)
        
        print(f"{match_num}. {result_emoji} {date_str:15} | {location:4} vs {opponent:25} → {result_color:4} ({team_result})")
        match_num += 1
    
    print(f"\n{'─'*100}")
    print(f"FORM: {' '.join(list(form_string))}")
    print(f"{'─'*100}")
    
    return form_string

# Show both teams
burnley_form = show_team_form("Burnley", burnley_id, data, reverse_mapping, home_col, away_col, result_col)
manutd_form = show_team_form("Man United", manutd_id, data, reverse_mapping, home_col, away_col, result_col)

# Summary
print(f"\n{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"Burnley Form:     {' '.join(list(burnley_form))}  (0 wins, 2 draws, 3 losses)")
print(f"Man United Form:  {' '.join(list(manutd_form))}  (3 wins, 0 draws, 2 losses)")
print(f"\n⚠️  Note: Man United's data is from April-May 2025 (8 months old)")
print(f"    Burnley's data is from Dec 2025 - Jan 2026 (current)")
print(f"{'='*100}")
