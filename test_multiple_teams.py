"""Test predictions with multiple teams to verify system is working."""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
django.setup()

from predictor.analytics import (
    calculate_probabilities_original, 
    get_team_recent_form_original,
    load_football_data,
    get_enhanced_features
)
from predictor.models import League, Team

def test_multiple_teams():
    """Test predictions with multiple different teams."""
    print("=" * 70)
    print("Testing Multiple Teams - Full System Check")
    print("=" * 70)
    
    # Test cases: (home_team, away_team, expected_category)
    test_cases = [
        ("Arsenal", "Aston Villa", "European Leagues"),
        ("Man City", "Liverpool", "European Leagues"),
        ("Barcelona", "Real Madrid", "European Leagues"),
        ("Grasshoppers", "Lausanne", "Others"),
        ("Basel", "Zurich", "Others"),
        ("Young Boys", "Lugano", "Others"),
    ]
    
    results = []
    
    for home_team, away_team, category in test_cases:
        print(f"\n{'='*70}")
        print(f"Test: {home_team} vs {away_team} ({category})")
        print(f"{'='*70}")
        
        try:
            # Determine which dataset to use
            other_teams = set()
            try:
                other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
                for league in other_leagues:
                    other_teams.update([team.name for team in league.teams.all()])
            except Exception:
                pass
            
            if home_team in other_teams and away_team in other_teams:
                dataset_num = 2
            else:
                dataset_num = 1
            
            print(f"Using Dataset {dataset_num}")
            data = load_football_data(dataset_num, use_cache=True)
            
            # Test 1: Form calculation
            print(f"\n1. Form Calculation:")
            home_form = get_team_recent_form_original(home_team, data, version="v1")
            away_form = get_team_recent_form_original(away_team, data, version="v1")
            print(f"   {home_team}: {home_form}")
            print(f"   {away_team}: {away_form}")
            
            # Test 2: Historical probabilities
            print(f"\n2. Historical Probabilities:")
            probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
            if probs:
                home_pct = probs.get("Home Team Win", 0)
                draw_pct = probs.get("Draw", 0)
                away_pct = probs.get("Away Team Win", 0)
                total = home_pct + draw_pct + away_pct
                
                print(f"   Home Win: {home_pct:.1f}%")
                print(f"   Draw:     {draw_pct:.1f}%")
                print(f"   Away Win: {away_pct:.1f}%")
                print(f"   Total:    {total:.1f}%")
                
                if abs(total - 100.0) < 0.1:
                    print(f"   ✅ Probabilities normalized correctly")
                else:
                    print(f"   ❌ Probabilities don't sum to 100%")
            else:
                print(f"   ⚠️  No probabilities returned (no H2H data)")
            
            # Test 3: Team strengths
            print(f"\n3. Team Strengths (Form-Based):")
            enhanced_features = get_enhanced_features(home_team, away_team)
            home_strength = enhanced_features['home_strength']
            away_strength = enhanced_features['away_strength']
            strength_diff = home_strength - away_strength
            
            print(f"   {home_team}: {home_strength:.3f}")
            print(f"   {away_team}: {away_strength:.3f}")
            print(f"   Strength Diff: {strength_diff:.3f}")
            
            if strength_diff > 0:
                print(f"   → {home_team} is stronger (home advantage)")
            elif strength_diff < 0:
                print(f"   → {away_team} is stronger (away advantage)")
            else:
                print(f"   → Teams are balanced")
            
            # Summary
            result = {
                'home': home_team,
                'away': away_team,
                'home_form': home_form,
                'away_form': away_form,
                'probs': probs,
                'strength_diff': strength_diff,
                'status': 'OK'
            }
            results.append(result)
            print(f"\n   ✅ Test passed")
            
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'home': home_team,
                'away': away_team,
                'status': f'ERROR: {str(e)}'
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r.get('status') == 'OK')
    failed = len(results) - passed
    
    print(f"\nTotal Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print(f"\n✅ All tests PASSED!")
    else:
        print(f"\n❌ Some tests FAILED!")
        for r in results:
            if r.get('status') != 'OK':
                print(f"   - {r['home']} vs {r['away']}: {r['status']}")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    test_multiple_teams()







