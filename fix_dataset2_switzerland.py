"""
Script to add Switzerland teams data to dataset2.csv
Extracts Switzerland data from lGIC/football_data2.csv and adds it to Football-main/data/football_data2.csv
"""
import pandas as pd
import os

def fix_dataset2():
    """Add Switzerland data to dataset2.csv"""
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    
    # Paths
    lgic_path = os.path.join(parent_dir, 'lGIC', 'football_data2.csv')
    main_dataset2_path = os.path.join(base_dir, 'data', 'football_data2.csv')
    
    print("=" * 70)
    print("Fixing Dataset2 - Adding Switzerland Teams")
    print("=" * 70)
    
    # Load lGIC dataset
    print(f"\n1. Loading lGIC dataset from: {lgic_path}")
    lgic_df = pd.read_csv(lgic_path)
    print(f"   Total rows in lGIC: {len(lgic_df)}")
    
    # Extract Switzerland data
    swiss_data = lgic_df[lgic_df['Country'] == 'Switzerland'].copy()
    print(f"   Switzerland rows found: {len(swiss_data)}")
    
    # Load current Football-main dataset2
    print(f"\n2. Loading Football-main dataset2 from: {main_dataset2_path}")
    main_df = pd.read_csv(main_dataset2_path)
    print(f"   Current rows in Football-main dataset2: {len(main_df)}")
    print(f"   Current columns: {main_df.columns.tolist()}")
    
    # Map columns from lGIC format to Football-main format
    print("\n3. Mapping columns...")
    mapped_swiss = pd.DataFrame()
    
    # Map the columns
    mapped_swiss['Date'] = swiss_data['Date']
    mapped_swiss['HomeTeam'] = swiss_data['Home']
    mapped_swiss['AwayTeam'] = swiss_data['Away']
    mapped_swiss['FTR'] = swiss_data['Res']  # Full Time Result
    mapped_swiss['HTR'] = ''  # Half Time Result - not available in lGIC data, leave empty
    mapped_swiss['Country'] = swiss_data['Country']
    mapped_swiss['League'] = swiss_data['League']
    mapped_swiss['Season'] = swiss_data['Season']
    mapped_swiss['Time'] = swiss_data['Time']
    
    print(f"   Mapped {len(mapped_swiss)} Switzerland rows")
    print(f"   Sample mapped row:")
    print(f"   {mapped_swiss.iloc[0].to_dict()}")
    
    # Check for duplicates (if Switzerland data already exists)
    print("\n4. Checking for existing Switzerland data...")
    existing_swiss = main_df[main_df['Country'] == 'Switzerland']
    if len(existing_swiss) > 0:
        print(f"   ⚠️  Found {len(existing_swiss)} existing Switzerland rows")
        print("   Removing duplicates before adding...")
        # Remove existing Switzerland data
        main_df = main_df[main_df['Country'] != 'Switzerland']
    
    # Combine datasets
    print("\n5. Combining datasets...")
    combined_df = pd.concat([main_df, mapped_swiss], ignore_index=True)
    print(f"   Total rows after combining: {len(combined_df)}")
    
    # Verify Switzerland teams are now present
    print("\n6. Verifying Switzerland teams...")
    swiss_teams = ['Basel', 'Zurich', 'Young Boys', 'Grasshoppers', 'Lausanne', 
                   'Lugano', 'Luzern', 'Servette', 'Sion', 'St. Gallen', 'Winterthur', 'Yverdon']
    
    swiss_matches = combined_df[
        (combined_df['HomeTeam'].isin(swiss_teams)) | 
        (combined_df['AwayTeam'].isin(swiss_teams))
    ]
    print(f"   Switzerland matches found: {len(swiss_matches)}")
    
    found_teams = set(combined_df[combined_df['HomeTeam'].isin(swiss_teams)]['HomeTeam'].unique()) | \
                  set(combined_df[combined_df['AwayTeam'].isin(swiss_teams)]['AwayTeam'].unique())
    print(f"   Switzerland teams found: {sorted(found_teams)}")
    
    # Save the updated dataset
    print("\n7. Saving updated dataset2...")
    combined_df.to_csv(main_dataset2_path, index=False)
    print(f"   [OK] Saved to: {main_dataset2_path}")
    
    print("\n" + "=" * 70)
    print("SUCCESS: Dataset2 has been updated with Switzerland teams!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  - Original rows: {len(main_df)}")
    print(f"  - Switzerland rows added: {len(mapped_swiss)}")
    print(f"  - Total rows now: {len(combined_df)}")
    print(f"  - Switzerland teams: {len(found_teams)}")
    print("=" * 70)

if __name__ == "__main__":
    fix_dataset2()

