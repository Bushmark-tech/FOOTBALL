import pandas as pd
try:
    df = pd.read_csv('data/football_data1.csv', encoding='latin-1')
    if 'HomeTeam' in df.columns:
        unique_teams = df['HomeTeam'].unique()
        print(f"Unique teams ({len(unique_teams)}):")
        print(unique_teams[:50])
        
        # Check types
        print(f"Data type: {df['HomeTeam'].dtype}")
        
    else:
        print("No HomeTeam column")
        print(df.columns)
except Exception as e:
    print(e)
