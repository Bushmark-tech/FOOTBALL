
import os
import sys
import pandas as pd
import joblib
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger('predictor.analytics')

sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
try:
    django.setup()
except Exception as e:
    print(f"Django setup warning: {e}")

from predictor.analytics import preprocess_for_models, load_football_data, load_team_mapping

def test_model2():
    print("=== Testing Model 2 Prediction (New Leagues) ===")
    
    # 1. Load Model 2
    try:
        model_path = 'models/model2.pkl'
        print(f"Loading {model_path}...")
        model2 = joblib.load(model_path)
        print("Model 2 loaded successfully.")
        
        if hasattr(model2, 'feature_names_in_'):
            print(f"Model expects {len(model2.feature_names_in_)} features.")
            
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 2. Load Data 2
    try:
        data = load_football_data(dataset=2)
        print(f"Data 2 loaded. Columns: {list(data.columns)[:10]}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 3. Test Fixtures from New Leagues
    fixtures = [
        ("Young Boys", "Basel"),          # Switzerland
        ("FC Copenhagen", "Aarhus"),      # Denmark
        ("Club America", "Cruz Azul"),    # Mexico
        ("Salzburg", "SK Rapid"),         # Austria
        ("Zenit", "Spartak Moscow"),      # Russia
        ("CFR Cluj", "FCSB")              # Romania
    ]
    
    for home_team, away_team in fixtures:
        print(f"\n=== Testing: {home_team} vs {away_team} ===")
        try:
            input_df = preprocess_for_models(home_team, away_team, model2, data)
            
            if input_df is not None:
                # Check for ID features (Model 2 specific)
                if 'HomeTeam' in input_df.columns:
                    hid = input_df['HomeTeam'].iloc[0]
                    aid = input_df['AwayTeam'].iloc[0]
                    print(f"  ID Check: HomeID={hid}, AwayID={aid}")
                
                # Check Form Features
                if 'home_points' in input_df.columns:
                     pts = input_df['home_points'].iloc[0]
                     msg = "Lookup OK" if pts > 0 else "Points=0"
                     print(f"  Form Check: Points={pts} [{msg}]")
                
                # Predict
                probs = model2.predict_proba(input_df)[0]
                pred_idx = probs.argmax()
                result = model2.classes_[pred_idx]
                
                outcome_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
                outcome = outcome_map.get(result, result)
                
                print(f"  Prediction: {outcome} (Probs: {probs})")
            else:
                print("  Preprocessing returned None.")
                
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_model2()
