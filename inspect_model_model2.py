import pickle
import joblib
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

model_path = 'models/model2.pkl'

try:
    print(f"Loading {model_path} with joblib...")
    model = joblib.load(model_path)
    print(f"SUCCESS with joblib")
    print(f"Type: {type(model)}")
except Exception as e:
    print(f"FAILED with joblib: {e}")
    try:
        print(f"Loading {model_path} with pickle...")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"SUCCESS with pickle")
    except Exception as e2:
        print(f"FAILED with pickle: {e2}")
