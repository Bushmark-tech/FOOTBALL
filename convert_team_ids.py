"""
Script to convert football data CSV files from team IDs to team names.
This will create new CSV files with actual team names instead of numeric IDs.
"""
import pandas as pd
import os

def convert_csv_with_team_names():
    """Convert football data CSVs from team IDs to team names."""
    
    # Load team mapping
    mapping_file = 'data/team_mapping.csv'
    if not os.path.exists(mapping_file):
        print(f"❌ Error: {mapping_file} not found!")
        return False
    
    print("=" * 70)
    print("CONVERTING FOOTBALL DATA CSV FILES")
    print("=" * 70)
    
    # Load team mapping
    print(f"\n📂 Loading team mapping from {mapping_file}...")
    team_mapping = pd.read_csv(mapping_file)
    
    # Create a dictionary for ID to Team name mapping
    id_to_team = dict(zip(team_mapping['ID'], team_mapping['Team']))
    print(f"✅ Loaded {len(id_to_team)} team mappings")
    
    # Convert both datasets
    datasets = [
        ('data/football_data1.csv', 'data/football_data1_with_names.csv'),
        ('data/football_data2.csv', 'data/football_data2_with_names.csv')
    ]
    
    for input_file, output_file in datasets:
        if not os.path.exists(input_file):
            print(f"\n⚠️  Skipping {input_file} (not found)")
            continue
        
        print(f"\n📊 Processing {input_file}...")
        
        # Load the data
        df = pd.read_csv(input_file, encoding='latin-1')
        print(f"   Total rows: {len(df)}")
        
        # Check which columns contain team IDs
        team_columns = []
        if 'HomeTeam' in df.columns:
            team_columns.append('HomeTeam')
        if 'AwayTeam' in df.columns:
            team_columns.append('AwayTeam')
        if 'Home' in df.columns:
            team_columns.append('Home')
        if 'Away' in df.columns:
            team_columns.append('Away')
        
        print(f"   Team columns found: {team_columns}")
        
        # Convert team IDs to names
        converted_count = 0
        for col in team_columns:
            if col in df.columns:
                # Check if column contains numeric IDs
                if df[col].dtype in ['int64', 'float64']:
                    print(f"   Converting {col} from IDs to names...")
                    df[col] = df[col].map(id_to_team)
                    # Fill any missing mappings with 'Unknown'
                    df[col] = df[col].fillna('Unknown')
                    converted_count += 1
                else:
                    print(f"   {col} already contains text (skipping)")
        
        if converted_count > 0:
            # Save the converted data
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"   ✅ Saved converted data to {output_file}")
            
            # Show sample
            print(f"\n   Sample converted data:")
            sample_cols = [col for col in team_columns if col in df.columns]
            if sample_cols:
                print(df[sample_cols].head(10).to_string())
        else:
            print(f"   ℹ️  No conversion needed (already has team names)")
    
    print("\n" + "=" * 70)
    print("CONVERSION COMPLETE!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print("1. Backup your original files if needed")
    print("2. Replace the original CSV files with the *_with_names.csv versions")
    print("3. Or update analytics.py to use the new files")
    print("\nTo use the new files, run:")
    print("  mv data/football_data1_with_names.csv data/football_data1.csv")
    print("  mv data/football_data2_with_names.csv data/football_data2.csv")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = convert_csv_with_team_names()
        if success:
            print("\n✅ SUCCESS! CSV files converted successfully!")
        else:
            print("\n❌ FAILED! Check the errors above.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
