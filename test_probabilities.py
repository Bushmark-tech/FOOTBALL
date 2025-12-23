"""Test that historical probabilities use form-based logic."""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import calculate_probabilities_original, load_football_data, get_enhanced_features

def test_form_based_probabilities():
    """Test that probabilities use form-based logic."""
    print("=" * 70)
    print("Testing Form-Based Historical Probabilities")
    print("=" * 70)
    
    home_team = "Grasshoppers"
    away_team = "Lausanne"
    
    # Load dataset 2
    data = load_football_data(2, use_cache=True)
    
    print(f"\nMatch: {home_team} vs {away_team}")
    
    # Calculate probabilities
    probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
    
    if probs:
        print(f"\nHistorical Probabilities (form-based):")
        print(f"  Home Win: {probs.get('Home Team Win', 0):.1f}%")
        print(f"  Draw:     {probs.get('Draw', 0):.1f}%")
        print(f"  Away Win: {probs.get('Away Team Win', 0):.1f}%")
        
        total = probs.get('Home Team Win', 0) + probs.get('Draw', 0) + probs.get('Away Team Win', 0)
        print(f"  Total:    {total:.1f}%")
        
        # Check team strengths
        enhanced_features = get_enhanced_features(home_team, away_team)
        print(f"\nTeam Strengths (form-based):")
        print(f"  {home_team}: {enhanced_features['home_strength']:.3f}")
        print(f"  {away_team}: {enhanced_features['away_strength']:.3f}")
        print(f"  Strength Diff: {enhanced_features['home_strength'] - enhanced_features['away_strength']:.3f}")
        
        if abs(total - 100.0) < 0.1:
            print("\n✅ Probabilities sum to 100% (normalized correctly)")
        else:
            print(f"\n❌ Probabilities don't sum to 100% (sum: {total:.1f}%)")
    else:
        print("\n❌ No probabilities returned")

if __name__ == "__main__":
    test_form_based_probabilities()

