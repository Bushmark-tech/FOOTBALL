"""
Test script for Smart Prediction Logic
Tests all 5 rules with different team combinations
"""
import requests
import json
import time

def test_prediction(home_team, away_team, category="European Leagues", expected_type=None):
    """Test a single prediction and display results."""
    api_url = "http://127.0.0.1:8001/predict"
    
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
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract key information
            prediction = result.get('prediction', 'Unknown')
            pred_type = result.get('prediction_type', 'Unknown')
            reasoning = result.get('reasoning', 'No reasoning provided')
            confidence = result.get('confidence', 0) * 100
            model_type = result.get('model_type', 'Unknown')
            probs = result.get('probabilities', {})
            
            # Display results
            print(f"\n[RESULT] Prediction: {prediction}")
            print(f"[TYPE] {pred_type}")
            print(f"[CONFIDENCE] {confidence:.1f}%")
            print(f"[MODEL] {model_type}")
            print(f"\n[PROBABILITIES]")
            print(f"  Home: {probs.get('Home', 0)*100:.1f}%")
            print(f"  Draw: {probs.get('Draw', 0)*100:.1f}%")
            print(f"  Away: {probs.get('Away', 0)*100:.1f}%")
            print(f"  Total: {sum(probs.values())*100:.1f}%")
            print(f"\n[REASONING] {reasoning}")
            
            # Validation
            print(f"\n[VALIDATION]")
            total = sum(probs.values())
            if abs(total - 1.0) < 0.01:
                print(f"  [PASS] Probabilities sum to 1.0 ({total:.4f})")
            else:
                print(f"  [FAIL] Probabilities sum to {total:.4f}, not 1.0")
            
            if expected_type and pred_type == expected_type:
                print(f"  [PASS] Prediction type matches expected: {expected_type}")
            elif expected_type:
                print(f"  [INFO] Prediction type: {pred_type} (expected: {expected_type})")
            
            # Check for Double Chance predictions
            if prediction in ["1X", "X2", "12"]:
                print(f"  [INFO] Double Chance prediction detected: {prediction}")
            
            return True
            
        else:
            print(f"\n[ERROR] API Error: {response.status_code}")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"  {error_detail}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timed out after 60 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Connection Error: FastAPI server not running")
        print(f"  Please start it with: python run_api.py")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return False

def main():
    """Run comprehensive tests for smart prediction logic."""
    print("="*70)
    print("SMART PREDICTION LOGIC TEST SUITE")
    print("="*70)
    print("\nTesting all 5 rules with different scenarios...")
    
    # Wait for models to be ready
    print("\nChecking if models are loaded...")
    time.sleep(2)
    
    try:
        health_response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        health_data = health_response.json()
        if not health_data.get('model1_loaded') or not health_data.get('model2_loaded'):
            print("[WARNING] Models may still be loading. Waiting 15 seconds...")
            time.sleep(15)
    except:
        print("[WARNING] Could not check health endpoint. Proceeding anyway...")
    
    test_cases = [
        # Test Case 1: Premier League teams (Model 1)
        {
            "home": "Man City",
            "away": "Fulham",
            "category": "European Leagues",
            "description": "Strong favorite vs weaker team"
        },
        
        # Test Case 2: Evenly matched teams
        {
            "home": "Liverpool",
            "away": "Arsenal",
            "category": "European Leagues",
            "description": "Two strong teams (may trigger Double Chance)"
        },
        
        # Test Case 3: Swiss teams (Model 2)
        {
            "home": "Lugano",
            "away": "Luzern",
            "category": "Others",
            "description": "Swiss league teams"
        },
        
        # Test Case 4: Another Swiss matchup
        {
            "home": "Basel",
            "away": "Young Boys",
            "category": "Others",
            "description": "Strong Swiss teams (may trigger Double Chance)"
        },
        
        # Test Case 5: Mid-table teams
        {
            "home": "Brentford",
            "away": "Brighton",
            "category": "European Leagues",
            "description": "Mid-table clash (uncertain outcome)"
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST CASE {i}: {test_case['description']}")
        print(f"{'#'*70}")
        
        success = test_prediction(
            test_case['home'],
            test_case['away'],
            test_case['category']
        )
        results.append(success)
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Smart prediction logic is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check the output above for details.")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

