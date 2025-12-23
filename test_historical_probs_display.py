"""
Test Historical Probabilities Display
Verify that Win Probability and Past Performance show different values
"""
import requests

# Test with Django web interface
django_url = "http://127.0.0.1:8000"

print("="*70)
print("TESTING HISTORICAL PROBABILITIES DISPLAY")
print("="*70)

# Make a prediction for Man City vs Liverpool (should have H2H data)
print("\nMaking prediction: Man City vs Liverpool")
print("This should show:")
print("  - Win Probability: Model predictions (after smart logic)")
print("  - Past Performance: Historical H2H data")

try:
    # First, make prediction via API
    api_response = requests.post(
        "http://127.0.0.1:8001/predict",
        json={
            "home_team": "Man City",
            "away_team": "Liverpool",
            "category": "European Leagues"
        },
        timeout=60
    )
    
    if api_response.status_code == 200:
        result = api_response.json()
        print(f"\n✅ API Prediction successful")
        print(f"   Model Probabilities:")
        probs = result.get('probabilities', {})
        print(f"     Man City: {probs.get('Home', 0)*100:.1f}%")
        print(f"     Draw: {probs.get('Draw', 0)*100:.1f}%")
        print(f"     Liverpool: {probs.get('Away', 0)*100:.1f}%")
        
        # Now check the result page
        print(f"\n📄 Check the result page in your browser:")
        print(f"   http://127.0.0.1:8000/result/?home_team=Man%20City&away_team=Liverpool&...")
        print(f"\n   Expected:")
        print(f"   ✅ Win Probability section: Shows model predictions")
        print(f"   ✅ Past Performance section: Shows DIFFERENT historical H2H data")
        print(f"   ✅ Both sections sum to 100%")
        
    else:
        print(f"\n❌ API Error: {api_response.status_code}")
        print(f"   {api_response.json().get('detail', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print(f"\n{'='*70}")
print("TO VERIFY THE FIX:")
print("="*70)
print("\n1. Open your browser and make a prediction for Man City vs Liverpool")
print("2. On the result page, compare:")
print("   - 'Win Probability' section (top)")
print("   - 'Past Performance' section (below)")
print("3. These should show DIFFERENT values:")
print("   - Win Probability = Model's prediction with smart logic")
print("   - Past Performance = Actual historical H2H data")
print("\n4. If both sections show the same values, the fix needs adjustment")
print("="*70)

