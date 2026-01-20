
import pickle
import joblib
import sys

model_path = 'models/model2.pkl'

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
except:
    model = joblib.load(model_path)

with open('model2_features.txt', 'w') as f:
    if hasattr(model, 'feature_names_in_'):
        f.write("\n".join(model.feature_names_in_))
    else:
        f.write("No feature names found")
