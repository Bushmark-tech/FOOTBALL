"""
Test Model 2 with Form-Based Predictions
Since football_data2.csv uses encoded IDs, we'll use form-based predictions
"""
import requests

api_url = "http://127.0.0.1:8001/predict"

print("="*70)
print("MODEL 2 FORM-BASED PREDICTION TEST")
print("="*70)
print("\nTesting Others category teams with form-based predictions...")
print("(No H2H data available due to encoded IDs in football_data2.csv)")

# Test Swiss teams
test_cases = [
    ("Basel", "Young Boys"),
    ("Lugano", "Luzern"),
    ("Servette", "Sion"),
]

for home, away in test_cases:
    print(f"\n{'='*70}")
    print(f"Testing: {home} vs {away}")
    print("="*70)
    
    try:
        response = requests.post(
            api_url,
            json={
                "home_team": home,
                "away_team": away,
                "category": "Others"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n[SUCCESS] Prediction completed (form-based)")
            print(f"  Prediction: {result.get('prediction')}")
            print(f"  Type: {result.get('prediction_type')}")
            print(f"  Confidence: {result.get('confidence', 0)*100:.1f}%")
            print(f"  Model: {result.get('model_type')}")
            
            probs = result.get('probabilities', {})
            print(f"\n  Probabilities:")
            print(f"    {home}: {probs.get('Home', 0)*100:.1f}%")
            print(f"    Draw: {probs.get('Draw', 0)*100:.1f}%")
            print(f"    {away}: {probs.get('Away', 0)*100:.1f}%")
            
            print(f"\n  Reasoning: {result.get('reasoning', 'N/A')}")
            
        else:
            print(f"\n[ERROR] {response.status_code}")
            print(f"  {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

print(f"\n{'='*70}")
print("CONCLUSION")
print("="*70)
print("\nIf predictions failed, the system needs form-based fallback.")
print("If predictions succeeded, form-based predictions are working!")
print("\nNote: Without H2H data, predictions are based on:")
print("  - Team name hashing (consistent strength)")
print("  - Form analysis")
print("  - Smart logic rules")
print("="*70)

