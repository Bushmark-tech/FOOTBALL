import pandas as pd

# Check both files
print("Checking football_data1.csv (CURRENT):")
df1 = pd.read_csv('data/football_data1.csv', encoding='latin-1')
print(f"  Rows: {len(df1)}")
print(f"  Columns: {len(df1.columns)}")
print(f"  Date range: {df1['Date'].min()} to {df1['Date'].max()}")

print("\nChecking football_data1_backup.csv (BACKUP):")
df2 = pd.read_csv('data/football_data1_backup.csv', encoding='latin-1')
print(f"  Rows: {len(df2)}")
print(f"  Columns: {len(df2.columns)}")
print(f"  Date range: {df2['Date'].min()} to {df2['Date'].max()}")

print(f"\nDifference: {len(df1) - len(df2)} rows")
print(f"\nCONCLUSION: System is using football_data1.csv with {len(df1)} rows")
