"""
Script to create a proper team name to ID mapping based on actual data in football_data2.csv
This will be used temporarily while we transition to using team names directly.
"""
import pandas as pd
import os

# Load football_data2.csv
data_path = 'data/football_data2.csv'
df = pd.read_csv(data_path)

# Load the team mapping to get team names
mapping_path = 'data/team_mapping.csv'
old_mapping = pd.read_csv(mapping_path, header=None, names=['TeamName', 'OldID'])

print("Creating reverse mapping from IDs in football_data2.csv to team names...")
print(f"Total rows in dataset: {len(df)}")

# Get all unique IDs from the dataset
home_ids = set(df['Home'].unique())
away_ids = set(df['Away'].unique())
all_dataset_ids = sorted(home_ids | away_ids)

print(f"Found {len(all_dataset_ids)} unique team IDs in football_data2.csv")
print(f"ID range: {min(all_dataset_ids)} to {max(all_dataset_ids)}")

# For now, we need to map team names from our database to the IDs that actually exist
# Since we don't have the original mapping, we'll need to infer it or use team names directly

print("\n⚠️  CRITICAL ISSUE:")
print("The team_mapping.csv uses IDs that don't exist in football_data2.csv")
print("Example: Man United → 234 (doesn't exist), Leeds → 212 (doesn't exist)")
print("\nSOLUTION: The system should use team NAMES directly, not IDs")
print("\nNext step: Modify analytics.py to work with team names instead of numeric IDs")
