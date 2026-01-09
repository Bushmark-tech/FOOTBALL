
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'football_data1.csv')

try:
    df = pd.read_csv(DATA_FILE, encoding='latin-1', low_memory=False)
    teams = sorted(df['HomeTeam'].dropna().unique().astype(str))
    print("Unique Teams (First 100):")
    print(teams[:100])
    
    print("\nSearch for 'Burnley':")
    print([t for t in teams if 'urnley' in t])
    
    print("\nSearch for 'City':")
    print([t for t in teams if 'City' in t])
except Exception as e:
    print(e)
