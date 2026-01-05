import pandas as pd
import os

# Load the data
data_path = 'data/football_data2.csv'
df = pd.read_csv(data_path)

# Get unique team IDs from Home and Away columns
home_ids = set(df['Home'].unique())
away_ids = set(df['Away'].unique())
all_ids = sorted(home_ids | away_ids)

print(f"Found {len(all_ids)} unique team IDs in football_data2.csv")
print(f"ID range: {min(all_ids)} to {max(all_ids)}")
print(f"\nFirst 20 IDs: {all_ids[:20]}")
print(f"\nSample rows:")
print(df[['Home', 'Away']].head(20))

# Check if Man United (234) or Leeds (212) exist
if 234 in all_ids:
    print("\n✓ ID 234 (Man United) EXISTS in dataset")
else:
    print("\n✗ ID 234 (Man United) NOT FOUND in dataset")
    
if 212 in all_ids:
    print("✓ ID 212 (Leeds) EXISTS in dataset")
else:
    print("✗ ID 212 (Leeds) NOT FOUND in dataset")
