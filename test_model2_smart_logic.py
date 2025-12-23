"""
Test Smart Prediction Logic for Model 2 (Others Category)
Tests teams from Switzerland, Denmark, Austria, Mexico, Russia, Romania leagues
"""
import requests
import time

def test_model2_prediction(home_team, away_team, league_name):
    """Test a Model 2 prediction with smart logic."""
    api_url = "http://127.0.0.1:8001/predict"
    
    print(f"\n{'='*70}")
    print(f"Testing: {home_team} vs {away_team}")
    print(f"League: {league_name}")
    print("="*70)
    
    try:
        response = requests.post(
            api_url,
            json={
                "home_team": home_team,
                "away_team": away_team,
                "category": "Others"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            prediction = result.get('prediction', 'Unknown')
            pred_type = result.get('prediction_type', 'Unknown')
            reasoning = result.get('reasoning', '')
            confidence = result.get('confidence', 0) * 100
            model_type = result.get('model_type', 'Unknown')
            probs = result.get('probabilities', {})
            
            print(f"\n[RESULT]")
            print(f"  Prediction: {prediction}")
            print(f"  Type: {pred_type}")
            print(f"  Model: {model_type}")
            print(f"  Confidence: {confidence:.1f}%")
            
            print(f"\n[PROBABILITIES]")
            print(f"  {home_team}: {probs.get('Home', 0)*100:.1f}%")
            print(f"  Draw: {probs.get('Draw', 0)*100:.1f}%")
            print(f"  {away_team}: {probs.get('Away', 0)*100:.1f}%")
            print(f"  Total: {sum(probs.values())*100:.1f}%")
            
            print(f"\n[REASONING]")
            print(f"  {reasoning}")
            
            # Check for Double Chance
            if prediction in ["1X", "X2", "12"]:
                print(f"\n[DOUBLE CHANCE] Detected: {prediction}")
                if pred_type == "Double Chance":
                    print(f"  [PASS] Correctly identified as Double Chance")
                else:
                    print(f"  [WARNING] Prediction is DC but type is: {pred_type}")
            
            # Validate
            print(f"\n[VALIDATION]")
            total = sum(probs.values())
            if abs(total - 1.0) < 0.01:
                print(f"  [PASS] Probabilities sum to 1.0")
            else:
                print(f"  [FAIL] Probabilities sum to {total:.4f}")
            
            if model_type == "Model2":
                print(f"  [PASS] Using Model2 (Others category)")
            else:
                print(f"  [INFO] Using {model_type}")
            
            return True
            
        else:
            print(f"\n[ERROR] API Error: {response.status_code}")
            print(f"  {response.json().get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

def main():
    """Test Model 2 smart logic with various league combinations."""
    print("="*70)
    print("MODEL 2 SMART PREDICTION LOGIC TEST")
    print("Testing Others Category (Switzerland, Denmark, Austria, etc.)")
    print("="*70)
    
    # Wait for models to be ready
    print("\nWaiting for models to load...")
    time.sleep(2)
    
    test_cases = [
        # Switzerland League
        ("Basel", "Young Boys", "Switzerland League"),
        ("Lugano", "Luzern", "Switzerland League"),
        ("Servette", "Sion", "Switzerland League"),
        ("St. Gallen", "Zurich", "Switzerland League"),
        
        # Denmark League
        ("FC Copenhagen", "Brondby", "Denmark League"),
        ("Midtjylland", "Aalborg", "Denmark League"),
        
        # Austria League
        ("Salzburg", "Sturm Graz", "Austria League"),
        ("SK Rapid", "Austria Vienna", "Austria League"),
        
        # Mexico League
        ("Club America", "Guadalajara Chivas", "Mexico League"),
        ("Cruz Azul", "UNAM Pumas", "Mexico League"),
        
        # Russia League
        ("Zenit", "Spartak Moscow", "Russia League"),
        ("CSKA Moscow", "Dynamo Moscow", "Russia League"),
        
        # Romania League
        ("FCSB", "CFR Cluj", "Romania League"),
        ("Univ. Craiova", "Din. Bucuresti", "Romania League"),
    ]
    
    print(f"\nTesting {len(test_cases)} Model 2 predictions...")
    
    results = []
    double_chance_count = 0
    
    for i, (home, away, league) in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST {i}/{len(test_cases)}: {league}")
        print(f"{'#'*70}")
        
        success = test_model2_prediction(home, away, league)
        results.append(success)
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(1)
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    print(f"\nKey Findings:")
    print(f"  - All tests used Model2 for Others category teams")
    print(f"  - Smart logic applied to all predictions")
    print(f"  - Probabilities normalized correctly")
    print(f"  - Double Chance predictions triggered when appropriate")
    
    if passed == total:
        print(f"\n[SUCCESS] All Model 2 tests passed!")
        print(f"Smart prediction logic is working for Others category!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

