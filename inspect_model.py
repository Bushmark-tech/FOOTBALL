import pickle
import pandas as pd
import sys
import os

# Add project root to path to handle custom classes if any
sys.path.append(os.getcwd())

model_path = 'models/model1.pkl'

try:
    print(f"Loading {model_path}...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Type: {type(model)}")
    print(f"Attributes: {dir(model)}")
    
    if hasattr(model, 'classes_'):
        print(f"Classes found: {len(model.classes_)}")
        print(model.classes_[:10])
    
    # Check if it's a pipeline
    if hasattr(model, 'named_steps'):
        print("Pipeline steps:", model.named_steps.keys())
    
    # Check for feature names
    if hasattr(model, 'feature_names_in_'):
        print("Features in:", model.feature_names_in_)
        
    # Check if there's an internal encoder
    # Sometimes encoders are saved separately or attached
    
except Exception as e:
    print(f"Error: {e}")
