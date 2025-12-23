"""
Test script to verify probability fix is working correctly.
Run this after starting the FastAPI server to test probability calculations.
"""
import requests
import json

def test_probability_normalization():
    """Test that probabilities are properly normalized and sum to 100%."""
    
    print("="*70)
    print("TESTING PROBABILITY FIX")
    print("="*70)
    
    # Test cases: (home_team, away_team, category)
    test_cases = [
        ("Man City", "Fulham", "European Leagues"),
        ("Liverpool", "Arsenal", "European Leagues"),
        ("Lugano", "Luzern", "Others"),
        ("Basel", "Young Boys", "Others"),
    ]
    
    api_url = "http://127.0.0.1:8001/predict"
    
    for home_team, away_team, category in test_cases:
        print(f"\n{'='*70}")
        print(f"Testing: {home_team} vs {away_team}")
        print(f"Category: {category}")
        print("="*70)
        
        try:
            response = requests.post(
                api_url,
                json={
                    "home_team": home_team,
                    "away_team": away_team,
                    "category": category
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract probabilities
                probs = result.get('probabilities', {})
                prob_home = probs.get('Home', 0)
                prob_draw = probs.get('Draw', 0)
                prob_away = probs.get('Away', 0)
                
                # Convert to percentages
                home_pct = prob_home * 100
                draw_pct = prob_draw * 100
                away_pct = prob_away * 100
                total_pct = home_pct + draw_pct + away_pct
                
                # Display results
                print(f"\n[OK] Prediction: {result.get('prediction', 'Unknown')}")
                print(f"     Model: {result.get('model_type', 'Unknown')}")
                print(f"     Confidence: {result.get('confidence', 0)*100:.1f}%")
                print(f"\n[PROBS] Probabilities (decimal format):")
                print(f"     Home: {prob_home:.4f}")
                print(f"     Draw: {prob_draw:.4f}")
                print(f"     Away: {prob_away:.4f}")
                print(f"     Sum:  {prob_home + prob_draw + prob_away:.4f}")
                print(f"\n[PROBS] Probabilities (percentage format):")
                print(f"     {home_team}: {home_pct:.1f}%")
                print(f"     Draw: {draw_pct:.1f}%")
                print(f"     {away_team}: {away_pct:.1f}%")
                print(f"     Total: {total_pct:.1f}%")
                
                # Validation checks
                print(f"\n[CHECK] Validation:")
                
                # Check 1: Probabilities sum to 1.0 (or very close)
                if abs((prob_home + prob_draw + prob_away) - 1.0) < 0.01:
                    print(f"     [PASS] Decimal sum is correct: {prob_home + prob_draw + prob_away:.4f} ~= 1.0")
                else:
                    print(f"     [FAIL] Decimal sum is incorrect: {prob_home + prob_draw + prob_away:.4f} != 1.0")
                
                # Check 2: Percentages sum to 100% (or very close)
                if abs(total_pct - 100.0) < 1.0:
                    print(f"     [PASS] Percentage sum is correct: {total_pct:.1f}% ~= 100%")
                else:
                    print(f"     [FAIL] Percentage sum is incorrect: {total_pct:.1f}% != 100%")
                
                # Check 3: All probabilities are in valid range (0-1)
                if 0 <= prob_home <= 1 and 0 <= prob_draw <= 1 and 0 <= prob_away <= 1:
                    print(f"     [PASS] All probabilities are in valid range (0-1)")
                else:
                    print(f"     [FAIL] Some probabilities are out of range!")
                    if prob_home < 0 or prob_home > 1:
                        print(f"            Home: {prob_home} (invalid)")
                    if prob_draw < 0 or prob_draw > 1:
                        print(f"            Draw: {prob_draw} (invalid)")
                    if prob_away < 0 or prob_away > 1:
                        print(f"            Away: {prob_away} (invalid)")
                
                # Check 4: Prediction matches highest probability
                max_prob = max(prob_home, prob_draw, prob_away)
                predicted_outcome = result.get('prediction', '')
                if (predicted_outcome == "Home" and prob_home == max_prob) or \
                   (predicted_outcome == "Draw" and prob_draw == max_prob) or \
                   (predicted_outcome == "Away" and prob_away == max_prob):
                    print(f"     [PASS] Prediction matches highest probability")
                else:
                    print(f"     [WARN] Prediction may not match highest probability")
                    print(f"            Predicted: {predicted_outcome}")
                    print(f"            Highest prob: Home={prob_home:.3f}, Draw={prob_draw:.3f}, Away={prob_away:.3f}")
                
            else:
                print(f"\n[ERROR] API Error: {response.status_code}")
                print(f"        {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Connection Error: FastAPI server not running")
            print(f"        Please start it with: python run_api.py")
            break
        except Exception as e:
            print(f"\n[ERROR] Error: {str(e)}")
    
    print(f"\n{'='*70}")
    print("TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_probability_normalization()

