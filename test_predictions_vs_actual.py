
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models, process_prediction_probabilities

# Define the actual results from the user's image
# Format: (Home Team, Away Team, Actual Outcome, Actual Score)
# Outcomes: 'Home', 'Draw', 'Away'
test_matches = [
    ("Man United", "Tottenham", "Home", "2-0"),
    ("Bournemouth", "Aston Villa", "Draw", "1-1"),
    ("Arsenal", "Sunderland", "Home", "3-0"),
    ("Burnley", "West Ham", "Away", "0-2"),
    ("Fulham", "Everton", "Away", "1-2"),
    ("Wolves", "Chelsea", "Away", "1-3"),
    ("Newcastle", "Brentford", "Away", "2-3")
]

def run_test():
    print("Loading models...")
    model1, model2 = load_prediction_models()
    print("Models loaded.\n")

    print(f"{'MATCH':<40} | {'PREDICTION':<20} | {'ACTUAL':<10} | {'STATUS'}")
    print("-" * 90)

    correct_count = 0
    total_matches = len(test_matches)

    for home, away, actual, score in test_matches:
        try:
            # Run prediction
            result = advanced_predict_match(home, away, model1, model2, category="European Leagues")
            
            if result:
                # Process probabilities to get final outcome (handle 1X, X2, 12, etc.)
                probs, outcome = process_prediction_probabilities(result)
                
                # Determine if prediction was correct
                is_correct = False
                
                # Mapping complex outcomes to simple actuals
                # Prediction '1X' covers 'Home' and 'Draw'
                # Prediction 'X2' covers 'Draw' and 'Away'
                # Prediction '12' covers 'Home' and 'Away'
                
                if outcome == "Home" and actual == "Home": is_correct = True
                elif outcome == "Away" and actual == "Away": is_correct = True
                elif outcome == "Draw" and actual == "Draw": is_correct = True
                
                # Double Chance Logic
                elif outcome == "1X" and (actual == "Home" or actual == "Draw"): is_correct = True
                elif outcome == "X2" and (actual == "Away" or actual == "Draw"): is_correct = True
                elif outcome == "12" and (actual == "Home" or actual == "Away"): is_correct = True
                
                status_icon = "✅ PASS" if is_correct else "❌ FAIL"
                if is_correct: correct_count += 1
                
                match_str = f"{home} vs {away}"
                print(f"{match_str:<40} | {outcome:<20} | {actual} ({score}) | {status_icon}")
                # print(f"   Probs: {probs}") 
            else:
                print(f"{home} vs {away} - Prediction Failed (No Data)")
                
        except Exception as e:
            print(f"Error testing {home} vs {away}: {e}")

    print("-" * 90)
    print(f"\nTotal Accuracy: {correct_count}/{total_matches} ({correct_count/total_matches*100:.1f}%)")

if __name__ == "__main__":
    run_test()
