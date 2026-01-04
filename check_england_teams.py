import pandas as pd

df = pd.read_csv('data/football_data1.csv')

print('='*60)
print('Checking Dataset Structure')
print('='*60)

# Check if Country column exists
if 'Country' in df.columns:
    print('\n✅ Country column EXISTS!')
    print('\nCountries in dataset:')
    print(df['Country'].value_counts().head(20))
    
    # Check England specifically
    england = df[df['Country'] == 'England']
    print(f'\n📊 England matches: {len(england)}')
    
    if len(england) > 0:
        print('\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Sample England teams (HomeTeam, AwayTeam):')
        print(england[['HomeTeam', 'AwayTeam']].head(20))
        
        # Check if these are team names or IDs
        sample_home = england['HomeTeam'].iloc[0]
        print(f'\n🔍 Sample HomeTeam value: {sample_home} (type: {type(sample_home).__name__})')
        
        # Get unique teams from England
        england_teams = set(england['HomeTeam'].unique()) | set(england['AwayTeam'].unique())
        print(f'\n📋 Total unique England teams: {len(england_teams)}')
        print('Sample teams:')
        for team in sorted(list(england_teams))[:15]:
            print(f'  - {team}')
    else:
        print('❌ No England matches found')
else:
    print('\n❌ No Country column in dataset')
    print(f'Available columns: {list(df.columns)[:20]}')
