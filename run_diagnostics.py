
import pandas as pd
import os

try:
    print("Starting diagnostics...")
    # 1. Load Mapping
    mapping_path = 'data/team_mapping.csv'
    if not os.path.exists(mapping_path):
        print(f"Error: {mapping_path} not found")
        exit(1)
        
    mapping = pd.read_csv(mapping_path)
    mapping['Team'] = mapping['Team'].astype(str).str.strip()
    mapping['ID'] = mapping['ID'].fillna(-1).astype(int)
    
    # Check for Collisions (Same ID, Different Names)
    id_counts = mapping.groupby('ID')['Team'].apply(list)
    collisions = id_counts[id_counts.apply(len) > 1]
    
    with open('data/mapping_diagnostics.txt', 'w', encoding='utf-8') as f:
        f.write('=== Mapping File Diagnostics ===\n')
        f.write(f'Total Rows: {len(mapping)}\n')
        f.write(f'Unique IDs: {len(mapping["ID"].unique())}\n')
        f.write(f'Unique Names: {len(mapping["Team"].unique())}\n')
        
        if not collisions.empty:
            f.write(f'\n[WARNING] {len(collisions)} IDs map to multiple teams (Possible Synonyms or Collisions):\n')
            # Sort by ID for readability
            for pid in sorted(collisions.index):
                teams = collisions[pid]
                f.write(f'ID {pid}: {", ".join(teams)}\n')
        
        # 2. Check Data Coverage
        mapped_ids = set(mapping['ID'].unique())
        
        # Define datasets to check
        datasets = [
            ('Data1', 'data/football_data1.csv', 'HomeTeam', 'AwayTeam'), 
            ('Data2', 'data/football_data2.csv', 'Home', 'Away')
        ]
        
        for name, fname, col1, col2 in datasets:
            if os.path.exists(fname):
                try:
                    # Use C engine for speed, skip bad lines if any
                    df = pd.read_csv(fname, encoding='latin-1', low_memory=False, on_bad_lines='skip')
                    
                    # Check columns exist
                    if col1 not in df.columns or col2 not in df.columns:
                        f.write(f'\n=== {name} Error ===\n')
                        f.write(f'Columns {col1}/{col2} not found in {fname}. Columns: {list(df.columns)}\n')
                        continue
                        
                    # Force numeric IDs
                    for col in [col1, col2]:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(-1).astype(int)
                    
                    # Collect all used IDs
                    ids = set(df[col1].unique()) | set(df[col2].unique())
                    ids.discard(-1) # Ignore invalid/NaN
                    
                    # Calc statistics
                    present = ids & mapped_ids
                    missing = ids - mapped_ids
                    
                    f.write(f'\n=== {name} Coverage ({fname}) ===\n')
                    f.write(f'Total Unique IDs used: {len(ids)}\n')
                    f.write(f'IDs present in Mapping: {len(present)}\n')
                    f.write(f'IDs MISSING from Mapping: {len(missing)}\n')
                    
                    if missing:
                        f.write('Missing IDs (First 50): ' + ', '.join(map(str, sorted(list(missing))[:50])) + '\n')
                        if len(missing) > 50:
                            f.write(f'... and {len(missing)-50} more.\n')
                            
                except Exception as e:
                    f.write(f'Error reading {name}: {e}\n')
            else:
                f.write(f'\n{name} file not found: {fname}\n')

    print('Diagnostics written to data/mapping_diagnostics.txt')

except Exception as e:
    print(f'Script Error: {e}')
