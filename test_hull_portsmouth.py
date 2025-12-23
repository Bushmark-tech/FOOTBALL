"""
Test Hull vs Portsmouth specifically to see the smart logic in action
"""
import requests

api_url = "http://127.0.0.1:8001/predict"

print("="*70)
print("Testing: Hull vs Portsmouth")
print("="*70)

response = requests.post(
    api_url,
    json={
        "home_team": "Hull",
        "away_team": "Portsmouth",
        "category": "European Leagues"
    },
    timeout=60
)

if response.status_code == 200:
    result = response.json()
    
    prediction = result.get('prediction')
    pred_type = result.get('prediction_type')
    reasoning = result.get('reasoning')
    confidence = result.get('confidence', 0) * 100
    probs = result.get('probabilities', {})
    model_type = result.get('model_type')
    
    print(f"\n{'='*70}")
    print("PREDICTION DETAILS")
    print("="*70)
    print(f"\nFinal Prediction: {prediction}")
    print(f"Prediction Type: {pred_type}")
    print(f"Model Used: {model_type}")
    print(f"Confidence: {confidence:.1f}%")
    
    print(f"\n{'='*70}")
    print("PROBABILITIES")
    print("="*70)
    print(f"Hull (Home):   {probs.get('Home', 0)*100:.1f}%")
    print(f"Draw:          {probs.get('Draw', 0)*100:.1f}%")
    print(f"Portsmouth:    {probs.get('Away', 0)*100:.1f}%")
    print(f"Total:         {sum(probs.values())*100:.1f}%")
    
    print(f"\n{'='*70}")
    print("REASONING")
    print("="*70)
    print(f"{reasoning}")
    
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print("="*70)
    
    # Check if this should be Double Chance
    if probs.get('Draw', 0) > 0.50:
        print(f"\n✓ Draw probability is HIGH ({probs.get('Draw', 0)*100:.1f}%)")
        if prediction == "Draw":
            print(f"  → Prediction: Draw (Single)")
            print(f"  → This is correct for a Draw prediction")
        elif prediction in ["1X", "X2"]:
            print(f"  → Prediction: {prediction} (Double Chance)")
            print(f"  → This is a safer bet given high draw probability")
        else:
            print(f"  → Prediction: {prediction}")
            print(f"  → Note: With 60% draw probability, this is risky")
    
    # Check probabilities distribution
    home_prob = probs.get('Home', 0)
    draw_prob = probs.get('Draw', 0)
    away_prob = probs.get('Away', 0)
    
    if abs(home_prob - away_prob) < 0.05 and draw_prob > 0.50:
        print(f"\n✓ Home and Away are very close ({home_prob*100:.1f}% vs {away_prob*100:.1f}%)")
        print(f"  → Draw is the clear favorite at {draw_prob*100:.1f}%")
        print(f"  → Single Draw prediction is appropriate")
    
    print(f"\n{'='*70}")
    print("VALIDATION")
    print("="*70)
    
    # Validate probabilities sum to 1.0
    total = sum(probs.values())
    if abs(total - 1.0) < 0.01:
        print(f"✓ Probabilities sum correctly: {total:.4f} ≈ 1.0")
    else:
        print(f"✗ Probabilities sum incorrectly: {total:.4f} ≠ 1.0")
    
    # Check prediction matches highest probability
    max_outcome = max(probs, key=probs.get)
    max_prob = probs[max_outcome]
    
    prediction_map = {
        "Home": "Home",
        "Draw": "Draw",
        "Away": "Away",
        "1X": "Home or Draw",
        "X2": "Draw or Away",
        "12": "Home or Away"
    }
    
    print(f"\nHighest probability: {max_outcome} ({max_prob*100:.1f}%)")
    print(f"Prediction: {prediction_map.get(prediction, prediction)}")
    
    if prediction == max_outcome or prediction in ["1X", "X2", "12"]:
        print(f"✓ Prediction is logical")
    else:
        print(f"⚠ Prediction differs from highest probability")
    
else:
    print(f"\nError: {response.status_code}")
    print(response.json())

print(f"\n{'='*70}")

