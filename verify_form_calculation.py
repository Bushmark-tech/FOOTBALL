"""Verify form calculation matches most recent matches."""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

import pandas as pd

# Load lGIC dataset 2
lgic_path = os.path.join('..', 'lGIC', 'football_data2.csv')
if not os.path.exists(lgic_path):
    lgic_path = os.path.join('lGIC', 'football_data2.csv')

d2 = pd.read_csv(lgic_path, encoding='latin-1')
d2['Date'] = pd.to_datetime(d2['Date'], errors='coerce', dayfirst=True)

print("=" * 70)
print("Verifying Form Calculation - Most Recent Matches")
print("=" * 70)

teams = ["Grasshoppers", "Lausanne"]

for team in teams:
    print(f"\n{'='*70}")
    print(f"Team: {team}")
    print(f"{'='*70}")
    
    # Get all matches for this team
    matches = d2[(d2['Home'] == team) | (d2['Away'] == team)]
    matches = matches.sort_values('Date', ascending=False).head(5)
    
    print(f"\nMost recent 5 matches (newest first):")
    form_chars = []
    
    for idx, row in matches.iterrows():
        date = row['Date']
        home_team = row['Home']
        away_team = row['Away']
        result = row['Res']
        
        is_home = home_team == team
        
        # Calculate form character
        if result == "D":
            form_char = "D"
        elif (result == "H" and is_home) or (result == "A" and not is_home):
            form_char = "W"
        else:
            form_char = "L"
        
        form_chars.append(form_char)
        
        opponent = away_team if is_home else home_team
        print(f"  {date.strftime('%Y-%m-%d')}: {team} {'(H)' if is_home else '(A)'} vs {opponent} = {result} -> {form_char}")
    
    calculated_form = "".join(form_chars)
    print(f"\nCalculated Form (most recent first): {calculated_form}")
    
    # Check manual form
    from predictor.analytics import MANUAL_FORM_LOOKUP
    if team in MANUAL_FORM_LOOKUP:
        manual_form = MANUAL_FORM_LOOKUP[team]
        print(f"Manual Form: {manual_form}")
        if calculated_form != manual_form:
            print(f"  ⚠️  DIFFERENT! Real data form: {calculated_form}, Manual: {manual_form}")
        else:
            print(f"  ✅ Forms match!")

print("\n" + "=" * 70)

