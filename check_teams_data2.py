import pandas as pd
try:
    df = pd.read_csv('data/football_data2.csv', encoding='latin-1')
    col = 'HomeTeam' if 'HomeTeam' in df.columns else 'Home'
    print(f"Using column: {col}")
    
    city = df[df[col] == 'Man City']
    print(f"Man City count: {len(city)}")
    
    utd = df[df[col] == 'Man United']
    print(f"Man United count: {len(utd)}")

except Exception as e:
    print(e)
