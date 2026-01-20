
import os
import sys
import pandas as pd
import joblib
import logging

# Setup logging to see our debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger('predictor.analytics')


# Add project root to path
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
try:
    django.setup()
except Exception as e:
    print(f"Django setup warning: {e}")

from predictor.analytics import preprocess_for_models, load_football_data, load_team_mapping

def test_model1():
    print("=== Testing Model 1 Prediction Structure ===")
    
    # 1. Load Model 1
    try:
        model_path = 'models/model1.pkl'
        if not os.path.exists(model_path):
            print(f"Error: {model_path} not found.")
            return
        
        print(f"Loading {model_path}...")
        model1 = joblib.load(model_path)
        print("Model 1 loaded successfully.")
        
        if hasattr(model1, 'feature_names_in_'):
            print(f"Model expects {len(model1.feature_names_in_)} features.")
            # Print first few features to see if they are One-Hot Strings or IDs
            print(f"Sample Features: {model1.feature_names_in_[:10]}")
            
            # Check for HomeTeam features
            home_feats = [f for f in model1.feature_names_in_ if 'HomeTeam' in f]
            if home_feats:
                print(f"Found {len(home_feats)} HomeTeam features. Example: {home_feats[0]}")
            else:
                print("No 'HomeTeam' string features found. (Likely purely numeric/ID based?)")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 2. Load Data (to verify it has IDs)
    try:
        data = load_football_data(dataset=1)
        if hasattr(data, 'columns'):
            print(f"Data 1 loaded. Columns: {list(data.columns)[:10]}")
            if 'HomeTeam' in data.columns:
                print(f"HomeTeam Sample: {data['HomeTeam'].head().tolist()}")
        else:
            print("Data 1 format unknown.")
    except Exception as e:
        print(f"Error loading data: {e}")

    # 3. Test Multiple Fixtures
    fixtures = [
        ("Young Boys", "Basel"),        # Swiss
        ("FC Copenhagen", "Aarhus"),    # Denmark (Collision ID 3?)
        ("Club America", "Cruz Azul"),  # Mexico
        ("Salzburg", "SK Rapid"),       # Austria
        ("Zenit", "Spartak Moscow")     # Russia
    ]
    
    for home_team, away_team in fixtures:
        print(f"\n=== Testing: {home_team} vs {away_team} ===")
        try:
            input_df = preprocess_for_models(home_team, away_team, model1, data)
            
            if input_df is not None:
                # Check mapping success
                if 'home_points' in input_df.columns:
                     pts = input_df['home_points'].iloc[0]
                     msg = "Lookup OK" if pts > 0 else "Points=0 (start of season or missing data?)"
                     print(f"  Mapping Check: Form Points = {pts} [{msg}]")
                
                # Predict
                probs = model1.predict_proba(input_df)[0]
                pred_idx = probs.argmax()
                result = model1.classes_[pred_idx]
                
                outcome_map = {0: "Away Win", 1: "Draw", 2: "Home Win"}
                outcome = outcome_map.get(result, result)
                
                print(f"  Prediction: {outcome} (Probs: {probs})")
            else:
                print("  Preprocessing returned None (Teams not found?)")
                
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_model1()
