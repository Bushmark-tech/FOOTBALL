
import os
import sys
import django
import pandas as pd
import numpy as np

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import load_football_data, preprocess_for_models, advanced_predict_match
from predictor.views import load_prediction_models

def verify_data():
    print("="*60)
    print("VERIFYING DATA INTEGRITY AND USAGE")
    print("="*60)

    # 1. Verify football_data1.csv (Dataset 1 for Model 1 - Main Leagues)
    print("\n[1] Verifying football_data1.csv (Dataset 1 - Model 1)")
    try:
        data1 = load_football_data(1, use_cache=False)
        print(f"    Loaded successfully. Shape: {data1.shape}")
        
        # Check for Critical Columns
        required_cols_v1 = ['HomeTeam', 'AwayTeam', 'FTR']
        missing = [col for col in required_cols_v1 if col not in data1.columns]
        if missing:
            print(f"    ERROR: Missing columns in v1: {missing}")
        else:
            print(f"    Verified columns: {required_cols_v1}")
            
        # Check for NaNs in critical columns
        nans_home = data1['HomeTeam'].isna().sum()
        nans_away = data1['AwayTeam'].isna().sum()
        nans_res = data1['FTR'].isna().sum()
        
        if nans_home + nans_away + nans_res > 0:
            print(f"    WARNING: Found NaNs in critical columns!")
            print(f"      HomeTeam NaNs: {nans_home}")
            print(f"      AwayTeam NaNs: {nans_away}")
            print(f"      Result NaNs:   {nans_res}")
        else:
            print(f"    PASSED: No NaNs in critical columns (HomeTeam, AwayTeam, FTR).")
            
        # Show first entry
        print(f"    Sample Row 0: {data1.iloc[0]['HomeTeam']} vs {data1.iloc[0]['AwayTeam']} -> Result: {data1.iloc[0]['FTR']}")

    except Exception as e:
        print(f"    ERROR loading dataset 1: {e}")

    # 2. Verify football_data2.csv (Dataset 2 for Model 2 - Other Leagues)
    print("\n[2] Verifying football_data2.csv (Dataset 2 - Model 2)")
    try:
        data2 = load_football_data(2, use_cache=False)
        print(f"    Loaded successfully. Shape: {data2.shape}")
        
        # Check for Critical Columns
        # v2 usually uses Home, Away, Res, but let's check what loaded
        required_cols_v2 = ['Home', 'Away', 'Res']
        missing_v2 = [col for col in required_cols_v2 if col not in data2.columns]
        
        # It might load in v1 format if normalized
        if missing_v2:
             print(f"    Note: Standard v2 columns not found, checking v1 format...")
             if 'HomeTeam' in data2.columns:
                 print("    Detected v1 format in Dataset 2 (HomeTeam/AwayTeam).")
             else:
                 print(f"    WARNING: Could not find standard columns in Dataset 2. Columns: {data2.columns.tolist()[:5]}...")
        else:
             print(f"    Verified columns: {required_cols_v2}")

        # Show first entry
        if 'Home' in data2.columns:
            print(f"    Sample Row 0: {data2.iloc[0]['Home']} vs {data2.iloc[0]['Away']} -> Result: {data2.iloc[0]['Res']}")
        elif 'HomeTeam' in data2.columns:
            print(f"    Sample Row 0: {data2.iloc[0]['HomeTeam']} vs {data2.iloc[0]['AwayTeam']} -> Result: {data2.iloc[0]['FTR']}")

    except Exception as e:
        print(f"    ERROR loading dataset 2: {e}")

    # 3. Simulate Model 1 Prediction Feature Generation
    print("\n[3] Testing Feature Generation for Model 1 (Main Leagues)")
    try:
        # Load models (mocks or real)
        print("    Loading prediction models...")
        model1, model2 = load_prediction_models()
        
        if model1:
            print("    Model 1 loaded. Testing feature generation...")
            home_team = "Arsenal"
            away_team = "Chelsea"
            
            # features = preprocess_for_models(home_team, away_team, model1, data=data1) # preprocess handles loading
            features = preprocess_for_models(home_team, away_team, model1)
            
            if features is not None:
                print(f"    Features generated successfully. Shape: {features.shape}")
                
                # Check for NaNs in features
                nan_features = features.isna().sum().sum()
                if nan_features > 0:
                    print(f"    WARNING: Generated features contain {nan_features} NaN values.")
                    print(f"    This confirms the user's concern about '1Nan'.")
                    # List columns with NaNs
                    nan_cols = features.columns[features.isna().any()].tolist()
                    print(f"    Columns with NaNs: {nan_cols}")
                else:
                    print(f"    PASSED: Generated features contain NO NaNs.")
            else:
                print("    WARNING: preprocess_for_models returned None.")
        else:
            print("    SKIPPING: Model 1 could not be loaded (missing .joblib file?).")

    except Exception as e:
        print(f"    ERROR during Model 1 simulation: {e}")

if __name__ == "__main__":
    verify_data()
