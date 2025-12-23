"""
Test script to diagnose prediction logic issues.
Tests the Arsenal vs Aston Villa prediction.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure stdout encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default

def safe_print(*args, **kwargs):
    """Print function that handles Windows encoding issues gracefully."""
    # Sanitize all arguments to remove problematic Unicode characters on Windows
    if sys.platform == 'win32':
        sanitized_args = []
        for arg in args:
            try:
                # Convert to string and remove non-ASCII characters that can't be encoded in cp1252
                arg_str = str(arg)
                # Replace common problematic Unicode characters with ASCII equivalents
                arg_str = arg_str.replace('\u2713', '[OK]')  # checkmark
                arg_str = arg_str.replace('\u2717', '[X]')   # cross mark
                arg_str = arg_str.replace('\u23f1', '')      # hourglass emoji part 1
                arg_str = arg_str.replace('\ufe0f', '')      # variation selector (emoji part)
                # Remove any remaining non-ASCII characters
                arg_str = arg_str.encode('ascii', 'ignore').decode('ascii')
                sanitized_args.append(arg_str)
            except Exception:
                # If sanitization fails, try to encode as ASCII
                try:
                    sanitized_args.append(str(arg).encode('ascii', 'ignore').decode('ascii'))
                except Exception:
                    sanitized_args.append('[ENCODING_ERROR]')
        args = tuple(sanitized_args)
    
    try:
        # Try normal print
        print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        # Fallback: encode to ASCII, ignoring non-ASCII characters
        try:
            message = ' '.join(str(arg).encode('ascii', 'ignore').decode('ascii') for arg in args)
            print(message, **kwargs)
        except Exception:
            # Last resort: print raw bytes to stderr
            try:
                message_bytes = ' '.join(str(arg) for arg in args).encode('ascii', 'ignore') + b'\n'
                sys.stderr.buffer.write(message_bytes)
            except Exception:
                pass  # Silently fail if even this doesn't work

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
import django
django.setup()

from predictor.analytics import (
    advanced_predict_match,
    get_team_recent_form_original,
    load_football_data,
    analytics_engine
)
import joblib

def test_prediction():
    """Test Arsenal vs Aston Villa prediction."""
    home_team = "Arsenal"
    away_team = "Aston Villa"
    
    safe_print("=" * 70)
    safe_print(f"Testing Prediction: {home_team} vs {away_team}")
    safe_print("=" * 70)
    
    # Load models
    safe_print("\n1. Loading Models...")
    try:
        model1_path = os.path.join(os.path.dirname(__file__), 'models', 'model1.pkl')
        model2_path = os.path.join(os.path.dirname(__file__), 'models', 'model2.pkl')
        
        model1 = None
        model2 = None
        
        if os.path.exists(model1_path):
            model1 = joblib.load(model1_path)
            safe_print(f"   [OK] Model 1 loaded")
        else:
            safe_print(f"   [X] Model 1 not found at {model1_path}")
        
        if os.path.exists(model2_path):
            model2 = joblib.load(model2_path)
            safe_print(f"   [OK] Model 2 loaded")
        else:
            safe_print(f"   [X] Model 2 not found at {model2_path}")
    except Exception as e:
        safe_print(f"   [ERROR] Error loading models: {e}")
        return
    
    # Get team form
    safe_print("\n2. Getting Team Form...")
    try:
        data = load_football_data(1, use_cache=True)
        home_form = get_team_recent_form_original(home_team, data, version="v1")
        away_form = get_team_recent_form_original(away_team, data, version="v1")
        safe_print(f"   {home_team} Form: {home_form}")
        safe_print(f"   {away_team} Form: {away_form}")
    except Exception as e:
        safe_print(f"   [ERROR] Error getting form: {e}")
        home_form = "DDDDD"
        away_form = "DDDDD"
    
    # Calculate team strengths
    safe_print("\n3. Calculating Team Strengths...")
    try:
        home_strength = analytics_engine.calculate_team_strength(home_team, 'home')
        away_strength = analytics_engine.calculate_team_strength(away_team, 'away')
        safe_print(f"   {home_team} Strength: {home_strength:.3f}")
        safe_print(f"   {away_team} Strength: {away_strength:.3f}")
        safe_print(f"   Strength Difference: {home_strength - away_strength:.3f}")
        
        # Expected prediction based on strength difference
        diff = home_strength - away_strength
        if diff < -0.12:
            expected = "Aston Villa Win (48% prob)"
        elif diff < -0.08:
            expected = "Aston Villa Win (42% prob)"
        elif abs(diff) < 0.03:
            expected = "Draw (34% prob)"
        elif diff > 0.12:
            expected = "Arsenal Win (48% prob)"
        else:
            expected = "Close match"
        safe_print(f"   Expected Prediction: {expected}")
    except Exception as e:
        safe_print(f"   [ERROR] Error calculating strengths: {e}")
    
    # Make prediction
    safe_print("\n4. Making Prediction...")
    try:
        result = advanced_predict_match(home_team, away_team, model1, model2)
        
        if result:
            safe_print(f"   [OK] Prediction made successfully")
            safe_print(f"\n   Results:")
            safe_print(f"   - Outcome: {result.get('outcome')}")
            safe_print(f"   - Model Type: {result.get('model_type')}")
            safe_print(f"   - Probabilities:")
            probs = result.get('probabilities', {})
            safe_print(f"     Home Win: {probs.get(0, probs.get('Home', 0)) * 100:.1f}%")
            safe_print(f"     Draw: {probs.get(1, probs.get('Draw', 0)) * 100:.1f}%")
            safe_print(f"     Away Win: {probs.get(2, probs.get('Away', 0)) * 100:.1f}%")
            safe_print(f"   - Confidence: {result.get('confidence', 0) * 100:.1f}%")
            
            # Check if prediction matches expected
            outcome = result.get('outcome')
            away_prob = probs.get(2, probs.get('Away', 0))
            home_prob = probs.get(0, probs.get('Home', 0))
            
            safe_print(f"\n   Analysis:")
            if away_prob > home_prob and away_prob > probs.get(1, probs.get('Draw', 0)):
                if outcome != "Away":
                    safe_print(f"   [WARNING] Model predicts {outcome}, but Away Win has highest probability ({away_prob*100:.1f}%)")
                else:
                    safe_print(f"   [OK] Prediction matches highest probability")
            elif home_prob > away_prob and home_prob > probs.get(1, probs.get('Draw', 0)):
                if outcome != "Home":
                    safe_print(f"   [WARNING] Model predicts {outcome}, but Home Win has highest probability ({home_prob*100:.1f}%)")
                else:
                    safe_print(f"   [OK] Prediction matches highest probability")
            else:
                safe_print(f"   [OK] Draw has highest probability")
        else:
            safe_print(f"   [X] Prediction returned None")
    except Exception as e:
        safe_print(f"   [ERROR] Error making prediction: {e}")
        import traceback
        traceback.print_exc()
    
    safe_print("\n" + "=" * 70)

if __name__ == "__main__":
    test_prediction()

