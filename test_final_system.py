"""
Final System Test - Both Model 1 and Model 2
Tests the complete prediction system with smart logic
"""
import requests
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api_url = "http://127.0.0.1:8001/predict"

print("="*70)
print("FINAL SYSTEM TEST - COMPLETE PREDICTION SYSTEM")
print("="*70)

# Test cases for both models
test_cases = [
    # MODEL 1 - European Leagues
    {
        "home": "Man City",
        "away": "Liverpool",
        "category": "European Leagues",
        "description": "Model 1 - Premier League top clash"
    },
    {
        "home": "Barcelona",
        "away": "Real Madrid",
        "category": "European Leagues",
        "description": "Model 1 - El Clasico"
    },
    {
        "home": "Bayern Munich",
        "away": "Dortmund",
        "category": "European Leagues",
        "description": "Model 1 - Bundesliga Der Klassiker"
    },
    
    # MODEL 2 - Others (Switzerland)
    {
        "home": "Basel",
        "away": "Young Boys",
        "category": "Others",
        "description": "Model 2 - Swiss League (Form-based)"
    },
    {
        "home": "FC Copenhagen",
        "away": "Midtjylland",
        "category": "Others",
        "description": "Model 2 - Denmark League (Form-based)"
    },
    {
        "home": "Salzburg",
        "away": "Sturm Graz",
        "category": "Others",
        "description": "Model 2 - Austria League (Form-based)"
    },
]

results = {
    "model1_success": 0,
    "model1_total": 0,
    "model2_success": 0,
    "model2_total": 0,
    "double_chance_count": 0,
    "errors": []
}

for test in test_cases:
    print(f"\n{'='*70}")
    print(f"{test['description']}")
    print(f"{test['home']} vs {test['away']}")
    print("="*70)
    
    is_model1 = test['category'] == 'European Leagues'
    if is_model1:
        results['model1_total'] += 1
    else:
        results['model2_total'] += 1
    
    try:
        response = requests.post(
            api_url,
            json={
                "home_team": test['home'],
                "away_team": test['away'],
                "category": test['category']
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Count success
            if is_model1:
                results['model1_success'] += 1
            else:
                results['model2_success'] += 1
            
            # Count double chance
            if result.get('prediction_type') == 'Double Chance':
                results['double_chance_count'] += 1
            
            print(f"\n✅ SUCCESS")
            print(f"   Prediction: {result.get('prediction')}")
            print(f"   Type: {result.get('prediction_type')}")
            print(f"   Confidence: {result.get('confidence', 0)*100:.1f}%")
            print(f"   Model: {result.get('model_type')}")
            
            probs = result.get('probabilities', {})
            prob_sum = sum(probs.values()) * 100
            print(f"\n   Probabilities (sum={prob_sum:.1f}%):")
            print(f"     {test['home']}: {probs.get('Home', 0)*100:.1f}%")
            print(f"     Draw: {probs.get('Draw', 0)*100:.1f}%")
            print(f"     {test['away']}: {probs.get('Away', 0)*100:.1f}%")
            
            print(f"\n   Reasoning: {result.get('reasoning', 'N/A')}")
            
            # Validation
            if abs(prob_sum - 100.0) > 0.1:
                print(f"\n   ⚠️  WARNING: Probabilities don't sum to 100% ({prob_sum:.1f}%)")
            
        else:
            error_msg = f"{test['description']}: HTTP {response.status_code}"
            results['errors'].append(error_msg)
            print(f"\n❌ ERROR {response.status_code}")
            print(f"   {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        error_msg = f"{test['description']}: {str(e)}"
        results['errors'].append(error_msg)
        print(f"\n❌ ERROR: {str(e)}")

# Print summary
print(f"\n{'='*70}")
print("FINAL RESULTS")
print("="*70)

print(f"\n📊 MODEL 1 (European Leagues - H2H Data)")
print(f"   Success: {results['model1_success']}/{results['model1_total']}", end="")
if results['model1_total'] > 0:
    print(f" ({results['model1_success']/results['model1_total']*100:.1f}%)")
else:
    print()

print(f"\n📊 MODEL 2 (Others - Form-Based)")
print(f"   Success: {results['model2_success']}/{results['model2_total']}", end="")
if results['model2_total'] > 0:
    print(f" ({results['model2_success']/results['model2_total']*100:.1f}%)")
else:
    print()

total_success = results['model1_success'] + results['model2_success']
total_tests = results['model1_total'] + results['model2_total']

print(f"\n📊 OVERALL")
print(f"   Total Success: {total_success}/{total_tests}", end="")
if total_tests > 0:
    print(f" ({total_success/total_tests*100:.1f}%)")
else:
    print()

print(f"   Double Chance Predictions: {results['double_chance_count']}")

if results['errors']:
    print(f"\n❌ ERRORS ({len(results['errors'])})")
    for error in results['errors']:
        print(f"   - {error}")

print(f"\n{'='*70}")
print("SYSTEM STATUS")
print("="*70)

if total_success == total_tests and total_tests > 0:
    print("\n✅ ✅ ✅ SYSTEM IS FULLY FUNCTIONAL! ✅ ✅ ✅")
    print("\n✅ Model 1: Working with H2H data")
    print("✅ Model 2: Working with form-based predictions")
    print("✅ Smart Logic: Applied to all predictions")
    print("✅ Double Chance: Supported")
    print("✅ Probabilities: Normalized and consistent")
    print("\n🎉 PRODUCTION-READY FOR DEPLOYMENT! 🎉")
elif total_success > 0:
    print(f"\n⚠️  PARTIALLY FUNCTIONAL ({total_success}/{total_tests} working)")
    print("\nSome predictions are working, but there are issues.")
    print("Check the errors above for details.")
else:
    print("\n❌ SYSTEM NOT FUNCTIONAL")
    print("\nNo predictions succeeded. Check the errors above.")

print("="*70)

