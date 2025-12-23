"""Quick test for Man City vs Fulham specifically."""
import requests

api_url = "http://127.0.0.1:8001/predict"

print("="*70)
print("Testing: Man City vs Fulham")
print("="*70)

response = requests.post(
    api_url,
    json={
        "home_team": "Man City",
        "away_team": "Fulham",
        "category": "European Leagues"
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    probs = result.get('probabilities', {})
    
    print(f"\nPrediction: {result.get('prediction')}")
    print(f"Model: {result.get('model_type')}")
    print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
    print(f"\nProbabilities (decimal):")
    print(f"  Man City: {probs.get('Home', 0):.4f}")
    print(f"  Draw: {probs.get('Draw', 0):.4f}")
    print(f"  Fulham: {probs.get('Away', 0):.4f}")
    print(f"  Sum: {sum(probs.values()):.4f}")
    print(f"\nProbabilities (percentage):")
    print(f"  Man City: {probs.get('Home', 0)*100:.1f}%")
    print(f"  Draw: {probs.get('Draw', 0)*100:.1f}%")
    print(f"  Fulham: {probs.get('Away', 0)*100:.1f}%")
    print(f"  Total: {sum(probs.values())*100:.1f}%")
    
    # Validation
    total = sum(probs.values())
    if abs(total - 1.0) < 0.01:
        print(f"\n[PASS] Probabilities sum to 1.0 correctly!")
    else:
        print(f"\n[FAIL] Probabilities sum to {total:.4f}, not 1.0!")
else:
    print(f"Error: {response.status_code}")
    print(response.json())

