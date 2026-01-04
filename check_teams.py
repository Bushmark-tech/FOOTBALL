import pandas as pd

# Load the dataset
df = pd.read_csv('data/football_data1.csv')

print(f'Total rows in dataset: {len(df)}')
print(f'Columns: {list(df.columns)[:10]}...')

# Check for Man City
print(f'\n{"="*60}')
print('Searching for "Man City"...')
man_city = df[(df['HomeTeam'].astype(str).str.contains('Man City', case=False, na=False)) | 
              (df['AwayTeam'].astype(str).str.contains('Man City', case=False, na=False))]
print(f'Found {len(man_city)} matches')
if len(man_city) > 0:
    print(man_city[['Date', 'HomeTeam', 'AwayTeam']].head())

# Check for Manchester
print(f'\n{"="*60}')
print('Searching for "Manchester"...')
manc = df[(df['HomeTeam'].astype(str).str.contains('Manchester', case=False, na=False)) | 
          (df['AwayTeam'].astype(str).str.contains('Manchester', case=False, na=False))]
print(f'Found {len(manc)} matches')
if len(manc) > 0:
    print('\nSample matches:')
    print(manc[['Date', 'HomeTeam', 'AwayTeam']].head(10))
    
    # Get unique team names
    teams = set(manc['HomeTeam'].unique()) | set(manc['AwayTeam'].unique())
    manchester_teams = [t for t in teams if 'manchester' in str(t).lower() or 'man' in str(t).lower()]
    print(f'\nManchester-related teams found: {manchester_teams}')

# Check what the actual team values look like
print(f'\n{"="*60}')
print('Sample team values (first 20 rows):')
print(df[['HomeTeam', 'AwayTeam']].head(20))

# Check if there's a Country column for European leagues
if 'Country' in df.columns:
    print(f'\n{"="*60}')
    print('Countries in dataset:')
    print(df['Country'].value_counts().head(10))
    
    # Check England specifically
    england = df[df['Country'] == 'England']
    print(f'\nEngland matches: {len(england)}')
    if len(england) > 0:
        print('Sample England teams:')
        print(england[['HomeTeam', 'AwayTeam']].head(10))
