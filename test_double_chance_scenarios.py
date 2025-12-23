"""
Test specific scenarios that should trigger Double Chance predictions
"""
import requests

def test_double_chance_scenario():
    """Test a scenario that should trigger Double Chance."""
    api_url = "http://127.0.0.1:8001/predict"
    
    # Test with teams that historically have high draw rates
    test_cases = [
        ("Chelsea", "Tottenham", "European Leagues"),
        ("Man United", "Newcastle", "European Leagues"),
        ("Everton", "Crystal Palace", "European Leagues"),
        ("Servette", "Sion", "Others"),  # Swiss teams
    ]
    
    print("="*70)
    print("TESTING DOUBLE CHANCE SCENARIOS")
    print("="*70)
    
    for home, away, category in test_cases:
        print(f"\n{'='*70}")
        print(f"Testing: {home} vs {away}")
        print("="*70)
        
        try:
            response = requests.post(
                api_url,
                json={
                    "home_team": home,
                    "away_team": away,
                    "category": category
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                prediction = result.get('prediction', 'Unknown')
                pred_type = result.get('prediction_type', 'Unknown')
                reasoning = result.get('reasoning', '')
                probs = result.get('probabilities', {})
                
                print(f"\nPrediction: {prediction}")
                print(f"Type: {pred_type}")
                print(f"Probabilities: Home={probs.get('Home', 0)*100:.1f}%, Draw={probs.get('Draw', 0)*100:.1f}%, Away={probs.get('Away', 0)*100:.1f}%")
                print(f"Reasoning: {reasoning}")
                
                if prediction in ["1X", "X2", "12"]:
                    print(f"\n✓ DOUBLE CHANCE DETECTED: {prediction}")
                else:
                    print(f"\n→ Single prediction: {prediction}")
                    
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print(f"\n{'='*70}")
    print("Note: Double Chance predictions depend on historical data.")
    print("If no Double Chance was triggered, the historical probabilities")
    print("may show clear winners for these matchups.")
    print("="*70)

if __name__ == "__main__":
    test_double_chance_scenario()

