import pickle
import pandas as pd
import sys
import os
import sklearn

print(f"Python version: {sys.version}")
print(f"Scikit-learn version: {sklearn.__version__}")

model_path = 'models/model1.pkl'

try:
    print(f"Loading {model_path}...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print("✅ Model loaded successfully!")
    print(f"Type: {type(model)}")
    
    encoder = None
    
    # Check if it's a Pipeline
    if hasattr(model, 'named_steps'):
        print("Pipeline detected. Steps:", model.named_steps.keys())
        # Look for 'labelencoder', 'encoder', or similar
        for step_name, step in model.named_steps.items():
            if 'encode' in step_name.lower():
                print(f"Found encoder step: {step_name}")
                encoder = step
                break
    
    # Check if it has classes_ directly
    if encoder is None and hasattr(model, 'classes_'):
        print("Model has classes_ attribute.")
        # This might be the target encoder (if it's a classifier)
        # But we need the input feature encoder for teams
        # Usually checking feature_names_in_ helps
        pass

    # In many setups, the team encoder isn't part of the model object,
    # but stored separately. If it's not here, we are stuck without the notebook.
    
    if hasattr(model, 'feature_names_in_'):
        print(f"Feature names ({len(model.feature_names_in_)}):")
        print(list(model.feature_names_in_)[:10])
        
        # Check if features are "HomeTeam_Man City" or just "HomeTeam"
        # If they are "HomeTeam_Man City", then it was One-Hot Encoded!
        # If so, we don't need a numeric ID map, we need to match the feature names.
        
except Exception as e:
    print(f"❌ Error: {e}")
