import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.models import Prediction

class MockPrediction:
    def __init__(self, outcome, prob_home=None, prob_draw=None, prob_away=None, home_team="Home", away_team="Away"):
        self.outcome = outcome
        self.prob_home = prob_home
        self.prob_draw = prob_draw
        self.prob_away = prob_away
        self.home_team = home_team
        self.away_team = away_team

def calculate_stats(predictions, home_team="Home", away_team="Away"):
    home_predictions = 0
    draw_predictions = 0
    away_predictions = 0
    total_predictions_count = 0

    for pred in predictions:
        total_predictions_count += 1
        winning_outcome = None
        
        # Check probabilities FIRST
        if pred.prob_home is not None and pred.prob_draw is not None and pred.prob_away is not None:
            try:
                p_h = float(pred.prob_home)
                p_d = float(pred.prob_draw)
                p_a = float(pred.prob_away)
                
                # Find max probability to determine the model's primary lean
                max_p = max(p_h, p_d, p_a)
                if max_p == p_h:
                    winning_outcome = 'Home'
                elif max_p == p_d:
                    winning_outcome = 'Draw'
                else:
                    winning_outcome = 'Away'
            except (ValueError, TypeError):
                winning_outcome = None
        
        # Fallback to Outcome String if no valid probabilities found
        if not winning_outcome:
            o = str(pred.outcome).strip()
            print(f"Checking outcome string: '{o}'")
            # Standard outcomes
            if o == 'Home' or o == f"{home_team} Win" or f"{home_team} Win" in o:
                winning_outcome = 'Home'
            elif o == 'Draw':
                winning_outcome = 'Draw'
            elif o == 'Away' or o == f"{away_team} Win" or f"{away_team} Win" in o:
                winning_outcome = 'Away'
            # Double Chance (Split weight if we don't have probabilities)
            elif o == '1X':
                home_predictions += 0.5
                draw_predictions += 0.5
                print("Matched 1X")
                continue
            elif o == 'X2':
                draw_predictions += 0.5
                away_predictions += 0.5
                print("Matched X2")
                continue
            elif o == '12':
                home_predictions += 0.5
                away_predictions += 0.5
                print("Matched 12")
                continue
        
        # Increment counts based on determined winning_outcome
        if winning_outcome == 'Home':
            home_predictions += 1
        elif winning_outcome == 'Draw':
            draw_predictions += 1
        elif winning_outcome == 'Away':
            away_predictions += 1
            
    print(f"Home: {home_predictions}, Draw: {draw_predictions}, Away: {away_predictions}")
    
    return {
        'total_count': total_predictions_count,
        'home_count': int(round(home_predictions, 1)) if round(home_predictions, 1) % 1 == 0 else round(home_predictions, 1),
        'draw_count': int(round(draw_predictions, 1)) if round(draw_predictions, 1) % 1 == 0 else round(draw_predictions, 1),
        'away_count': int(round(away_predictions, 1)) if round(away_predictions, 1) % 1 == 0 else round(away_predictions, 1),
    }

print("Test 1: 1X Outcome with no probabilities")
p1 = MockPrediction(outcome="1X")
stats1 = calculate_stats([p1])
print(stats1)

print("\nTest 2: 1X Outcome WITH probabilities (should prefer probabilities)")
p2 = MockPrediction(outcome="1X", prob_home=0.3, prob_draw=0.3, prob_away=0.4)
stats2 = calculate_stats([p2])
print(stats2)

print("\nTest 3: 1X Outcome WITH probabilities favoring Home")
p3 = MockPrediction(outcome="1X", prob_home=0.5, prob_draw=0.3, prob_away=0.2)
stats3 = calculate_stats([p3])
print(stats3)
