
import os
import sys
import django
from unittest.mock import MagicMock
import pandas as pd

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import calculate_probabilities_model2, load_football_data

# Mock data with 1 match
data = pd.DataFrame({
    'HomeTeam': ['Wolves'],
    'AwayTeam': ['Chelsea'],
    'FTR': ['D'],
    'FTHG': [1],
    'FTAG': [1],
    'Date': ['01/01/2024']
})

# Test with 1 match
print("Testing with 1 match (Wolves vs Chelsea)...")
probs = calculate_probabilities_model2('Wolves', 'Chelsea', data, "v1")
print(f"Probabilities (expect None): {probs}")

# Mock data with 2 matches
data2 = pd.DataFrame({
    'HomeTeam': ['Wolves', 'Wolves'],
    'AwayTeam': ['Chelsea', 'Chelsea'],
    'FTR': ['D', 'A'],
    'FTHG': [1, 0],
    'FTAG': [1, 2],
    'Date': ['01/01/2024', '01/02/2024']
})

# Test with 2 matches
print("\nTesting with 2 matches...")
probs2 = calculate_probabilities_model2('Wolves', 'Chelsea', data2, "v1")
print(f"Probabilities (expect dict): {probs2}")
