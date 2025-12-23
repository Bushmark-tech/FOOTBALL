"""
Comprehensive model diagnostic to find the real issue.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')

import django
django.setup()

import joblib
import numpy as np
from predictor.analytics import (
    advanced_predict_match,
    preprocess_for_models,
    load_football_data,
    calculate_probabilities_original
)

print("="*70)
print("MODEL DIAGNOSTIC TOOL")
print("="*70)

# Step 1: Load the model
print("\n[STEP 1] Loading Model...")
try:
    model = joblib.load('models/model1.pkl')
    print(f"[OK] Model loaded: {type(model)}")
    print(f"[OK] Has predict_proba: {hasattr(model, 'predict_proba')}")
    print(f"[OK] Has classes_: {hasattr(model, 'classes_')}")
    if hasattr(model, 'classes_'):
        print(f"[OK] Classes: {model.classes_}")
    if hasattr(model, 'n_features_in_'):
        print(f"[OK] Expected features: {model.n_features_in_}")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    sys.exit(1)

# Step 2: Load data
print("\n[STEP 2] Loading Football Data...")
try:
    data = load_football_data(1, use_cache=False)
    print(f"[OK] Data loaded: {len(data)} rows")
    print(f"[OK] Columns: {list(data.columns)[:10]}...")
except Exception as e:
    print(f"[ERROR] Failed to load data: {e}")
    sys.exit(1)

# Step 3: Test feature preparation for different teams
print("\n[STEP 3] Testing Feature Preparation...")
test_matches = [
    ("Chelsea", "Brighton"),
    ("Man City", "Liverpool"),
    ("Arsenal", "Tottenham"),
]

features_dict = {}
for home, away in test_matches:
    print(f"\n--- {home} vs {away} ---")
    try:
        features = preprocess_for_models(home, away, model, data)
        if features is not None:
            print(f"[OK] Features shape: {features.shape}")
            print(f"[OK] Features (first 10): {features[0][:10]}")
            print(f"[OK] Features (last 10): {features[0][-10:]}")
            features_dict[f"{home}_vs_{away}"] = features
        else:
            print(f"[ERROR] Features returned None!")
    except Exception as e:
        print(f"[ERROR] Feature preparation failed: {e}")
        import traceback
        traceback.print_exc()

# Step 4: Check if features are identical
print("\n[STEP 4] Checking Feature Uniqueness...")
if len(features_dict) >= 2:
    keys = list(features_dict.keys())
    feat1 = features_dict[keys[0]]
    feat2 = features_dict[keys[1]]
    
    if np.array_equal(feat1, feat2):
        print(f"[ERROR] Features are IDENTICAL for different matches!")
        print(f"[ERROR] This is why all predictions are the same!")
    else:
        print(f"[OK] Features are DIFFERENT for different matches")
        diff_count = np.sum(feat1 != feat2)
        print(f"[OK] Number of different features: {diff_count} out of {feat1.shape[1]}")

# Step 5: Test model predictions
print("\n[STEP 5] Testing Model Predictions...")
for match_name, features in features_dict.items():
    print(f"\n--- {match_name} ---")
    try:
        # Get prediction
        pred = model.predict(features)
        print(f"[OK] Prediction: {pred[0]} (0=Away, 1=Draw, 2=Home)")
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)
            print(f"[OK] Probabilities: {proba[0]}")
            print(f"    Away: {proba[0][0]:.4f} ({proba[0][0]*100:.2f}%)")
            print(f"    Draw: {proba[0][1]:.4f} ({proba[0][1]*100:.2f}%)")
            print(f"    Home: {proba[0][2]:.4f} ({proba[0][2]*100:.2f}%)")
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()

# Step 6: Test historical probabilities
print("\n[STEP 6] Testing Historical Probabilities...")
for home, away in test_matches:
    print(f"\n--- {home} vs {away} ---")
    try:
        hist_probs = calculate_probabilities_original(home, away, data, version="v1")
        if hist_probs:
            print(f"[OK] Historical probabilities:")
            print(f"    Home: {hist_probs.get('Home Team Win', 0):.2f}%")
            print(f"    Draw: {hist_probs.get('Draw', 0):.2f}%")
            print(f"    Away: {hist_probs.get('Away Team Win', 0):.2f}%")
        else:
            print(f"[WARN] No historical data found")
    except Exception as e:
        print(f"[ERROR] Historical probability calculation failed: {e}")

# Step 7: Test full prediction pipeline
print("\n[STEP 7] Testing Full Prediction Pipeline...")
for home, away in test_matches[:2]:  # Test first 2
    print(f"\n--- {home} vs {away} ---")
    try:
        result = advanced_predict_match(home, away, model, None)
        if result:
            print(f"[OK] Outcome: {result.get('outcome')}")
            print(f"[OK] Confidence: {result.get('confidence'):.4f}")
            probs = result.get('probabilities', {})
            print(f"[OK] Probabilities:")
            print(f"    0 (Away): {probs.get(0, 0):.4f}")
            print(f"    1 (Draw): {probs.get(1, 0):.4f}")
            print(f"    2 (Home): {probs.get(2, 0):.4f}")
        else:
            print(f"[ERROR] Prediction returned None!")
    except Exception as e:
        print(f"[ERROR] Full prediction failed: {e}")
        import traceback
        traceback.print_exc()

# Step 8: Diagnosis Summary
print("\n" + "="*70)
print("DIAGNOSIS SUMMARY")
print("="*70)

# Check if features are identical
if len(features_dict) >= 2:
    keys = list(features_dict.keys())
    all_same = True
    first_feat = features_dict[keys[0]]
    
    for key in keys[1:]:
        if not np.array_equal(first_feat, features_dict[key]):
            all_same = False
            break
    
    if all_same:
        print("\n[CRITICAL] ISSUE FOUND:")
        print("  - All matches have IDENTICAL features")
        print("  - This causes identical predictions")
        print("  - Problem: Feature preparation not team-specific")
        print("\nSOLUTION:")
        print("  - Check preprocess_for_models() function")
        print("  - Ensure team names are one-hot encoded")
        print("  - Ensure team-specific stats are included")
    else:
        print("\n[OK] Features are different for different matches")
        print("\nIf predictions are still identical, check:")
        print("  - Model training quality")
        print("  - Feature importance")
        print("  - determine_final_prediction() logic")

print("\n" + "="*70)

