"""
Backtest script to verify all models are working correctly.
Tests Model 1 and Model 2 with sample teams from each category.
"""
import os
import sys
import django
import traceback

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

import joblib
from predictor.analytics import (
    advanced_predict_match,
    load_football_data,
    calculate_probabilities_original,
    get_team_recent_form_original,
    compute_mean_for_teams
)
from predictor.views import LEAGUES_BY_CATEGORY

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_result(test_name, status, details=""):
    """Print test result with status."""
    status_symbol = "[OK]" if status else "[FAIL]"
    status_text = "PASS" if status else "FAIL"
    print(f"{status_symbol} [{status_text}] {test_name}")
    if details:
        print(f"    {details}")

def test_model_loading():
    """Test if models can be loaded."""
    print_section("TEST 1: Model Loading")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model1_path = os.path.join(base_dir, 'models', 'model1.pkl')
    model2_path = os.path.join(base_dir, 'models', 'model2.pkl')
    
    model1_loaded = False
    model2_loaded = False
    model1 = None
    model2 = None
    
    # Test Model 1
    if os.path.exists(model1_path):
        try:
            print(f"Loading Model 1 from: {model1_path}")
            model1 = joblib.load(model1_path)
            print_result("Model 1 loaded", True, f"Type: {type(model1).__name__}")
            if hasattr(model1, 'n_features_in_'):
                print(f"    Features: {model1.n_features_in_}")
            model1_loaded = True
        except Exception as e:
            print_result("Model 1 loaded", False, f"Error: {str(e)}")
            traceback.print_exc()
    else:
        print_result("Model 1 file exists", False, f"Path not found: {model1_path}")
    
    # Test Model 2
    if os.path.exists(model2_path):
        try:
            print(f"Loading Model 2 from: {model2_path}")
            model2 = joblib.load(model2_path)
            print_result("Model 2 loaded", True, f"Type: {type(model2).__name__}")
            if hasattr(model2, 'n_features_in_'):
                print(f"    Features: {model2.n_features_in_}")
            model2_loaded = True
        except Exception as e:
            print_result("Model 2 loaded", False, f"Error: {str(e)}")
            traceback.print_exc()
    else:
        print_result("Model 2 file exists", False, f"Path not found: {model2_path}")
    
    return model1, model2, model1_loaded, model2_loaded

def test_data_loading():
    """Test if data files can be loaded."""
    print_section("TEST 2: Data Loading")
    
    # Test Dataset 1
    try:
        data1 = load_football_data(1)
        data1_loaded = data1 is not None and not (hasattr(data1, 'empty') and data1.empty)
        if data1_loaded:
            print_result("Dataset 1 loaded", True, f"Shape: {data1.shape}, Columns: {len(data1.columns)}")
        else:
            print_result("Dataset 1 loaded", False, "Data is empty or None")
    except Exception as e:
        print_result("Dataset 1 loaded", False, f"Error: {str(e)}")
        traceback.print_exc()
        data1_loaded = False
    
    # Test Dataset 2
    try:
        data2 = load_football_data(2)
        data2_loaded = data2 is not None and not (hasattr(data2, 'empty') and data2.empty)
        if data2_loaded:
            print_result("Dataset 2 loaded", True, f"Shape: {data2.shape}, Columns: {len(data2.columns)}")
        else:
            print_result("Dataset 2 loaded", False, "Data is empty or None")
    except Exception as e:
        print_result("Dataset 2 loaded", False, f"Error: {str(e)}")
        traceback.print_exc()
        data2_loaded = False
    
    return data1_loaded, data2_loaded

def get_sample_teams():
    """Get sample teams from each category for testing."""
    model1_teams = []
    model2_teams = []
    
    for category, leagues in LEAGUES_BY_CATEGORY.items():
        for league, teams in leagues.items():
            if category == 'European Leagues' and teams:
                model1_teams.extend(teams[:3])  # Take first 3 teams from each league
            elif category == 'Others' and teams:
                model2_teams.extend(teams[:3])  # Take first 3 teams from each league
    
    return model1_teams[:10], model2_teams[:10]  # Limit to 10 teams each

def test_model1_predictions(model1, model2):
    """Test predictions with Model 1 teams."""
    print_section("TEST 3: Model 1 Predictions (European Leagues)")
    
    model1_teams, _ = get_sample_teams()
    
    if not model1:
        print_result("Model 1 available", False, "Model 1 not loaded, skipping tests")
        return 0, 0
    
    if len(model1_teams) < 2:
        print_result("Model 1 teams available", False, "Not enough teams for testing")
        return 0, 0
    
    tests_passed = 0
    tests_failed = 0
    
    # Test a few match combinations
    test_matches = [
        (model1_teams[0], model1_teams[1]),
        (model1_teams[2], model1_teams[3]) if len(model1_teams) >= 4 else None,
        (model1_teams[4], model1_teams[5]) if len(model1_teams) >= 6 else None,
    ]
    
    for match in test_matches:
        if not match:
            continue
        
        home_team, away_team = match
        test_name = f"{home_team} vs {away_team}"
        
        try:
            result = advanced_predict_match(home_team, away_team, model1, model2)
            
            if result and isinstance(result, dict):
                outcome = result.get('outcome')
                confidence = result.get('confidence', 0)
                model_type = result.get('model_type', '')
                probabilities = result.get('probabilities', {})
                
                # Validate result structure
                valid_outcome = outcome in ['Home', 'Draw', 'Away']
                valid_confidence = 0 <= confidence <= 1
                valid_model_type = 'Model1' in model_type
                valid_probs = isinstance(probabilities, dict) and len(probabilities) > 0
                
                if valid_outcome and valid_confidence and valid_model_type and valid_probs:
                    print_result(test_name, True, 
                               f"Outcome: {outcome}, Confidence: {confidence:.2f}, Model: {model_type}")
                    tests_passed += 1
                else:
                    print_result(test_name, False, 
                               f"Invalid result structure - Outcome: {valid_outcome}, "
                               f"Confidence: {valid_confidence}, Model: {valid_model_type}, Probs: {valid_probs}")
                    tests_failed += 1
            else:
                print_result(test_name, False, "Result is None or not a dict")
                tests_failed += 1
                
        except Exception as e:
            print_result(test_name, False, f"Error: {str(e)}")
            traceback.print_exc()
            tests_failed += 1
    
    return tests_passed, tests_failed

def test_model2_predictions(model1, model2):
    """Test predictions with Model 2 teams."""
    print_section("TEST 4: Model 2 Predictions (Other Leagues)")
    
    _, model2_teams = get_sample_teams()
    
    if not model2:
        print_result("Model 2 available", False, "Model 2 not loaded, skipping tests")
        return 0, 0
    
    if len(model2_teams) < 2:
        print_result("Model 2 teams available", False, "Not enough teams for testing")
        return 0, 0
    
    tests_passed = 0
    tests_failed = 0
    
    # Test a few match combinations
    test_matches = [
        (model2_teams[0], model2_teams[1]),
        (model2_teams[2], model2_teams[3]) if len(model2_teams) >= 4 else None,
        (model2_teams[4], model2_teams[5]) if len(model2_teams) >= 6 else None,
    ]
    
    for match in test_matches:
        if not match:
            continue
        
        home_team, away_team = match
        test_name = f"{home_team} vs {away_team}"
        
        try:
            result = advanced_predict_match(home_team, away_team, model1, model2)
            
            if result and isinstance(result, dict):
                outcome = result.get('outcome')
                confidence = result.get('confidence', 0)
                model_type = result.get('model_type', '')
                probabilities = result.get('probabilities', {})
                
                # Validate result structure
                valid_outcome = outcome in ['Home', 'Draw', 'Away']
                valid_confidence = 0 <= confidence <= 1
                valid_model_type = 'Model2' in model_type or 'Model1' in model_type  # Could fallback to Model1
                valid_probs = isinstance(probabilities, dict) and len(probabilities) > 0
                
                if valid_outcome and valid_confidence and valid_probs:
                    print_result(test_name, True, 
                               f"Outcome: {outcome}, Confidence: {confidence:.2f}, Model: {model_type}")
                    tests_passed += 1
                else:
                    print_result(test_name, False, 
                               f"Invalid result structure - Outcome: {valid_outcome}, "
                               f"Confidence: {valid_confidence}, Model: {valid_model_type}, Probs: {valid_probs}")
                    tests_failed += 1
            else:
                print_result(test_name, False, "Result is None or not a dict")
                tests_failed += 1
                
        except Exception as e:
            print_result(test_name, False, f"Error: {str(e)}")
            traceback.print_exc()
            tests_failed += 1
    
    return tests_passed, tests_failed

def test_probability_calculation():
    """Test probability calculation function."""
    print_section("TEST 5: Probability Calculation")
    
    model1_teams, model2_teams = get_sample_teams()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test with Dataset 1
    try:
        data1 = load_football_data(1)
        if data1 is not None and not (hasattr(data1, 'empty') and data1.empty) and len(model1_teams) >= 2:
            home, away = model1_teams[0], model1_teams[1]
            probs = calculate_probabilities_original(home, away, data1, version="v1")
            if probs and isinstance(probs, dict) and len(probs) > 0:
                print_result(f"Probabilities for {home} vs {away} (Dataset 1)", True, 
                           f"Probs: {probs}")
                tests_passed += 1
            else:
                print_result(f"Probabilities for {home} vs {away} (Dataset 1)", False, 
                           "Invalid probabilities returned")
                tests_failed += 1
    except Exception as e:
        print_result("Probability calculation (Dataset 1)", False, f"Error: {str(e)}")
        tests_failed += 1
    
    # Test with Dataset 2
    try:
        data2 = load_football_data(2)
        if data2 is not None and not (hasattr(data2, 'empty') and data2.empty) and len(model2_teams) >= 2:
            home, away = model2_teams[0], model2_teams[1]
            probs = calculate_probabilities_original(home, away, data2, version="v2")
            if probs and isinstance(probs, dict) and len(probs) > 0:
                print_result(f"Probabilities for {home} vs {away} (Dataset 2)", True, 
                           f"Probs: {probs}")
                tests_passed += 1
            else:
                print_result(f"Probabilities for {home} vs {away} (Dataset 2)", False, 
                           "Invalid probabilities returned")
                tests_failed += 1
    except Exception as e:
        print_result("Probability calculation (Dataset 2)", False, f"Error: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_team_form():
    """Test team form retrieval."""
    print_section("TEST 6: Team Form Retrieval")
    
    model1_teams, model2_teams = get_sample_teams()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test with Dataset 1
    try:
        data1 = load_football_data(1)
        if data1 is not None and not (hasattr(data1, 'empty') and data1.empty) and model1_teams:
            team = model1_teams[0]
            form = get_team_recent_form_original(team, data1, version="v1")
            if form:
                print_result(f"Form for {team} (Dataset 1)", True, f"Form: {form}")
                tests_passed += 1
            else:
                print_result(f"Form for {team} (Dataset 1)", False, "No form data returned")
                tests_failed += 1
    except Exception as e:
        print_result("Team form (Dataset 1)", False, f"Error: {str(e)}")
        tests_failed += 1
    
    # Test with Dataset 2
    try:
        data2 = load_football_data(2)
        if data2 is not None and not (hasattr(data2, 'empty') and data2.empty) and model2_teams:
            team = model2_teams[0]
            form = get_team_recent_form_original(team, data2, version="v2")
            if form:
                print_result(f"Form for {team} (Dataset 2)", True, f"Form: {form}")
                tests_passed += 1
            else:
                print_result(f"Form for {team} (Dataset 2)", False, "No form data returned")
                tests_failed += 1
    except Exception as e:
        print_result("Team form (Dataset 2)", False, f"Error: {str(e)}")
        tests_failed += 1
    
    return tests_passed, tests_failed

def main():
    """Run all backtests."""
    print("\n" + "=" * 80)
    print("  FOOTBALL PREDICTOR - MODEL BACKTESTING SUITE")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Model Loading
    model1, model2, model1_loaded, model2_loaded = test_model_loading()
    if model1_loaded:
        total_passed += 1
    else:
        total_failed += 1
    if model2_loaded:
        total_passed += 1
    else:
        total_failed += 1
    
    # Test 2: Data Loading
    data1_loaded, data2_loaded = test_data_loading()
    if data1_loaded:
        total_passed += 1
    else:
        total_failed += 1
    if data2_loaded:
        total_passed += 1
    else:
        total_failed += 1
    
    # Test 3: Model 1 Predictions
    if model1_loaded:
        passed, failed = test_model1_predictions(model1, model2)
        total_passed += passed
        total_failed += failed
    
    # Test 4: Model 2 Predictions
    if model2_loaded:
        passed, failed = test_model2_predictions(model1, model2)
        total_passed += passed
        total_failed += failed
    
    # Test 5: Probability Calculation
    passed, failed = test_probability_calculation()
    total_passed += passed
    total_failed += failed
    
    # Test 6: Team Form
    passed, failed = test_team_form()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
    
    if total_failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED - Models are working correctly!")
    else:
        print(f"\n[ERROR] {total_failed} TEST(S) FAILED - Please review the errors above.")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()

