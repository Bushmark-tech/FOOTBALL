"""
Simple script to test API performance and see timing output.
Run this to test prediction speed and see debug output.
"""
import requests
import time
import json

API_URL = "http://127.0.0.1:8001/predict"

def test_prediction(home_team, away_team, category=None):
    """Test a prediction and measure time."""
    print(f"\n{'='*70}")
    print(f"Testing: {home_team} vs {away_team}")
    print(f"{'='*70}")
    
    payload = {
        "home_team": home_team,
        "away_team": away_team,
    }
    if category:
        payload["category"] = category
    
    start_time = time.time()
    
    try:
        print(f"Sending request to {API_URL}...")
        response = requests.post(
            API_URL,
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Total Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nPrediction Result:")
            print(f"  Outcome: {result.get('prediction', 'N/A')}")
            print(f"  Score: {result.get('home_score', 'N/A')} - {result.get('away_score', 'N/A')}")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
            print(f"  Model Type: {result.get('model_type', 'N/A')}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n❌ REQUEST TIMED OUT after {elapsed:.2f} seconds!")
        print("This means the API took too long to respond.")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Error: {e}")
        print(f"Time elapsed: {elapsed:.2f} seconds")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("API Performance Test Script")
    print("="*70)
    print("\nThis script will test the API and show timing information.")
    print("Check the FastAPI console for detailed [PERF] timing logs.\n")
    
    # Test with a few different teams
    test_cases = [
        ("Lugano", "Luzern", "Others"),  # Model 2 teams
        ("Man City", "Liverpool", "European Leagues"),  # Model 1 teams
        ("Arsenal", "Chelsea", "European Leagues"),  # Model 1 teams
    ]
    
    for home, away, cat in test_cases:
        test_prediction(home, away, cat)
        time.sleep(1)  # Small delay between tests
    
    print(f"\n{'='*70}")
    print("Testing Complete!")
    print("="*70)
    print("\nTo see detailed timing breakdown:")
    print("1. Check the FastAPI console (where you ran 'python run_api.py')")
    print("2. Look for lines starting with [PERF] or [DEBUG]")
    print("3. The [PERF] lines show timing for each operation")
    print("\nExample output:")
    print("  [PERF] Prediction timings: {'load_data_1': 2.5, 'calculate_probabilities': 15.3, 'total': 19.0}")
    print("\nThe operation with the highest time is the bottleneck!")

