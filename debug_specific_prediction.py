
import os
import sys
import django
import pandas as pd
import numpy as np

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import (
    advanced_predict_match, 
    load_football_data, 
    preprocess_for_models,
    calculate_probabilities_model2
)
from predictor.views import load_prediction_models

def debug_prediction():
    print("DEBUGGING PREDICTION FOR YOUNG BOYS vs BASEL")
    
    # 1. Load Data
    data = load_football_data(2, use_cache=False)
    print(f"Data Loaded: {data.shape}")
    
    home_team = "Young Boys"
    away_team = "Basel"
    
    # 2. Check Probabilities (H2H)
    print("\n--- Checking H2H Probabilities ---")
    probs = calculate_probabilities_model2(home_team, away_team, data)
    print(f"Probabilities: {probs}")
    
    if probs is None:
        print("CRITICAL: calculate_probabilities_model2 returned None!")
    
    # 3. Check Model Loading
    print("\n--- Checking Models ---")
    model1, model2 = load_prediction_models()
    print(f"Model 2: {model2}")
    
    # 4. Check Feature Generation
    print("\n--- Checking Feature Generation ---")
    try:
        features = preprocess_for_models(home_team, away_team, model2, data=data)
        if features is not None:
            print(f"Features generated! Shape: {features.shape}")
            print(features.iloc[0].to_dict())
        else:
            print("CRITICAL: preprocess_for_models returned None!")
    except Exception as e:
        print(f"ERROR during feature generation: {e}")

if __name__ == "__main__":
    debug_prediction()
