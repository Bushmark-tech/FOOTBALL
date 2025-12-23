"""Check which dataset contains Grasshoppers and Lausanne."""
import pandas as pd
import os

print("=" * 70)
print("Checking Data Files")
print("=" * 70)

# Check dataset 1
d1_path = 'data/football_data1.csv'
d2_path = 'data/football_data2.csv'

if os.path.exists(d1_path):
    try:
        d1 = pd.read_csv(d1_path, encoding='utf-8')
    except:
        d1 = pd.read_csv(d1_path, encoding='latin-1')
    print(f"\nDataset 1: {len(d1)} rows")
    
    if 'HomeTeam' in d1.columns:
        home_col = 'HomeTeam'
        away_col = 'AwayTeam'
    elif 'Home' in d1.columns:
        home_col = 'Home'
        away_col = 'Away'
    else:
        print("  Cannot find team columns")
        home_col = None
    
    if home_col:
        # Check for Grasshoppers
        grass_home = d1[d1[home_col].astype(str).str.contains('Grass', case=False, na=False)]
        grass_away = d1[d1[away_col].astype(str).str.contains('Grass', case=False, na=False)]
        print(f"  Grasshoppers matches: {len(grass_home)} home, {len(grass_away)} away")
        
        # Check for Lausanne
        laus_home = d1[d1[home_col].astype(str).str.contains('Laus', case=False, na=False)]
        laus_away = d1[d1[away_col].astype(str).str.contains('Laus', case=False, na=False)]
        print(f"  Lausanne matches: {len(laus_home)} home, {len(laus_away)} away")
        
        if len(grass_home) > 0 or len(grass_away) > 0:
            print("\n  ✅ Grasshoppers found in Dataset 1!")
            # Show recent matches
            if len(grass_home) > 0:
                recent = grass_home.tail(5)
                print(f"  Recent home matches (last 5):")
                for idx, row in recent.iterrows():
                    result_col = 'FTR' if 'FTR' in row.index else 'Res'
                    result = row.get(result_col, '?')
                    print(f"    vs {row[away_col]}: {result}")
        
        if len(laus_home) > 0 or len(laus_away) > 0:
            print("\n  ✅ Lausanne found in Dataset 1!")
            # Show recent matches
            if len(laus_home) > 0:
                recent = laus_home.tail(5)
                print(f"  Recent home matches (last 5):")
                for idx, row in recent.iterrows():
                    result_col = 'FTR' if 'FTR' in row.index else 'Res'
                    result = row.get(result_col, '?')
                    print(f"    vs {row[away_col]}: {result}")

if os.path.exists(d2_path):
    try:
        d2 = pd.read_csv(d2_path, encoding='utf-8')
    except:
        d2 = pd.read_csv(d2_path, encoding='latin-1')
    print(f"\nDataset 2: {len(d2)} rows")
    
    if 'HomeTeam' in d2.columns:
        home_col = 'HomeTeam'
        away_col = 'AwayTeam'
    elif 'Home' in d2.columns:
        home_col = 'Home'
        away_col = 'Away'
    else:
        home_col = None
    
    if home_col:
        grass_home = d2[d2[home_col].astype(str).str.contains('Grass', case=False, na=False)]
        grass_away = d2[d2[away_col].astype(str).str.contains('Grass', case=False, na=False)]
        print(f"  Grasshoppers matches: {len(grass_home)} home, {len(grass_away)} away")
        
        laus_home = d2[d2[home_col].astype(str).str.contains('Laus', case=False, na=False)]
        laus_away = d2[d2[away_col].astype(str).str.contains('Laus', case=False, na=False)]
        print(f"  Lausanne matches: {len(laus_home)} home, {len(laus_away)} away")

print("\n" + "=" * 70)

