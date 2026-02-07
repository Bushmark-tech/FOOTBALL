
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

# Combined test matches (EPL + La Liga + Bundesliga)
# Format: (Home, Away, Actual Outcome[Home/Draw/Away], Score)
all_test_matches = [
    # EPL Batch
    ("Man United", "Tottenham", "Home", "2-0"),
    ("Bournemouth", "Aston Villa", "Draw", "1-1"),
    ("Arsenal", "Sunderland", "Home", "3-0"),
    ("Burnley", "West Ham", "Away", "0-2"),
    ("Fulham", "Everton", "Away", "1-2"),
    ("Wolves", "Chelsea", "Away", "1-3"),
    ("Newcastle", "Brentford", "Away", "2-3"),
    
    # La Liga / Bundesliga Batch
    ("Barcelona", "Mallorca", "Home", "3-0"),
    ("Sociedad", "Elche", "Home", "3-1"),
    ("Heidenheim", "Hamburg", "Away", "0-2"),
    ("Freiburg", "Werder Bremen", "Home", "1-0"),
    ("Mainz", "Augsburg", "Home", "2-0"),
    ("St Pauli", "Stuttgart", "Home", "2-1"),
    ("Wolfsburg", "Dortmund", "Away", "1-2"),
    ("M'gladbach", "Leverkusen", "Draw", "1-1")
]

def run_comprehensive_test():
    print("Loading prediction models...")
    model1, model2 = load_prediction_models()
    print("Models loaded successfully.\n")
    
    # Table Header
    # Match | System Prediction | Actual Result | Accuracy
    print(f"{'Match':<30} | {'System Prediction':<20} | {'Actual Result':<15} | {'Accuracy'}")
    print("-" * 85)

    correct_count = 0
    total_matches = len(all_test_matches)

    for home, away, actual, score in all_test_matches:
        try:
            # Run prediction
            result = advanced_predict_match(home, away, model1, model2, category="European Leagues")
            
            if result:
                # Process probabilities
                probs, outcome = process_prediction_probabilities(result)
                
                # Check correctness (Exact + Double Chance coverage)
                is_correct = False
                
                if outcome == "Home" and actual == "Home": is_correct = True
                elif outcome == "Away" and actual == "Away": is_correct = True
                elif outcome == "Draw" and actual == "Draw": is_correct = True
                elif outcome == "1X" and (actual == "Home" or actual == "Draw"): is_correct = True
                elif outcome == "X2" and (actual == "Away" or actual == "Draw"): is_correct = True
                elif outcome == "12" and (actual == "Home" or actual == "Away"): is_correct = True
                
                status_icon = "✅ PASS" if is_correct else "❌ FAIL"
                if is_correct: correct_count += 1
                
                # Format Prediction text for table
                # outcome e.g. "Home", "1X", "Away" -> "Home Win", "1X (Home/Draw)", "Away Win"
                pred_display = outcome
                if outcome == "Home": pred_display = "Home Win"
                elif outcome == "Away": pred_display = "Away Win"
                elif outcome == "1X": pred_display = "1X (Home/Draw)"
                elif outcome == "X2": pred_display = "X2 (Away/Draw)"
                
                match_str = f"{home} vs {away}"
                actual_display = f"{actual} ({score})"
                
                print(f"{match_str:<30} | {pred_display:<20} | {actual_display:<15} | {status_icon}")
            else:
                print(f"{home} vs {away}".ljust(30) + " | " + "No Data".ljust(20) + " | " + "Unknown".ljust(15) + " | ❌ ERROR")
                
        except Exception as e:
             print(f"{home} vs {away}".ljust(30) + " | " + "Error".ljust(20) + " | " + str(e)[:15] + " | ❌ ERROR")

    print("-" * 85)
    accuracy = (correct_count / total_matches) * 100
    print(f"Summary: {correct_count}/{total_matches} Correct ({accuracy:.1f}%)")

if __name__ == "__main__":
    run_comprehensive_test()
