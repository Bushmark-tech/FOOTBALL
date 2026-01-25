"""
Quick Model1 Production Test
Simple test to evaluate if Model1 is production-ready
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import advanced_predict_match
from predictor.views import load_prediction_models

# Test matches - European League teams
test_matches = [
    ("Man United", "Liverpool", "European Leagues"),
    ("Arsenal", "Chelsea", "European Leagues"),
    ("Barcelona", "Real Madrid", "European Leagues"),
    ("Bayern Munich", "Dortmund", "European Leagues"),
    ("PSG", "Marseille", "European Leagues"),
]

print("="*70)
print("🏆 MODEL 1 QUICK PRODUCTION TEST")
print("="*70)
print()

# Load models
model1, model2 = load_prediction_models()

results = []
for home, away, category in test_matches:
    print(f"Testing: {home} vs {away}")
    
    try:
        result = advanced_predict_match(home, away, model1, model2, category=category)
        
        if result:
            outcome = result.get('outcome')
            confidence = result.get('confidence', 0)
            probs = result.get('probabilities', {})
            model_used = result.get('model_type')
            
            # Get probabilities
            home_prob = probs.get(2, probs.get('Home', 0)) * 100
            draw_prob = probs.get(1, probs.get('Draw', 0)) * 100
            away_prob = probs.get(0, probs.get('Away', 0)) * 100
            
            print(f"  ✅ Prediction: {outcome}")
            print(f"  📊 Probabilities: H:{home_prob:.1f}% D:{draw_prob:.1f}% A:{away_prob:.1f}%")
            print(f"  🤖 Model: {model_used}")
            print(f"  💪 Confidence: {confidence:.1%}")
            
            results.append({
                'match': f"{home} vs {away}",
                'outcome': outcome,
                'draw_prob': draw_prob,
                'model': model_used
            })
        else:
            print(f"  ❌ No prediction returned")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()

# Analysis
print("="*70)
print("📊 ANALYSIS")
print("="*70)
print()

if results:
    # Count outcomes
    outcomes = [r['outcome'] for r in results]
    draw_count = outcomes.count('Draw')
    draw_pct = (draw_count / len(outcomes)) * 100
    
    # Average draw probability
    avg_draw_prob = sum(r['draw_prob'] for r in results) / len(results)
    
    # Model usage
    model1_count = sum(1 for r in results if r['model'] == 'Model1')
    
    print(f"Total Tests: {len(results)}")
    print(f"Draw Predictions: {draw_count} ({draw_pct:.1f}%)")
    print(f"Average Draw Probability: {avg_draw_prob:.1f}%")
    print(f"Model1 Usage: {model1_count}/{len(results)}")
    print()
    
    # Production readiness
    print("🎯 PRODUCTION READINESS:")
    if draw_pct > 60:
        print("  ❌ HIGH DRAW BIAS - Model may need retraining")
    elif draw_pct > 40:
        print("  ⚠️  MODERATE DRAW BIAS - Monitor closely")
    else:
        print("  ✅ GOOD VARIETY in predictions")
    
    if model1_count == len(results):
        print("  ✅ Model1 is being used correctly for European leagues")
    else:
        print(f"  ⚠️  Model2 used {len(results) - model1_count} times (should be 0)")
    
    if avg_draw_prob < 35:
        print("  ✅ Draw probabilities are reasonable")
    else:
        print("  ⚠️  Draw probabilities are high - model may be uncertain")
else:
    print("❌ No successful predictions")

print()
print("="*70)
