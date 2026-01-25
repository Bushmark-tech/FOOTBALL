import logging
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Prediction, Team, League, BillingUsage
from .auth_views import use_prediction_credit, check_subscription_status
from .analytics import (
    analytics_engine, 
    advanced_predict_match, 
    safe_import_numpy
)
from .utils import normalize_team_name
import traceback

logger = logging.getLogger(__name__)

# --- API Endpoints ---

@csrf_exempt
def api_predict(request):
    """API endpoint for making predictions.
    
    Expects POST with JSON body:
        {
            "home_team": "Team A",
            "away_team": "Team B",
            "category": "League Name" (Optional)
        }
    Returns JSON prediction result.
    """
    if request.method == 'POST':
        try:
            # Handle both JSON and Form Data
            data = {}
            
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                     return JsonResponse({'error': 'Invalid JSON body'}, status=400)
            else:
                # Form data (application/x-www-form-urlencoded or multipart/form-data)
                data = request.POST.dict()
            
            # Extract fields validation
            home_team = data.get('home_team')
            away_team = data.get('away_team')
            category = data.get('category')
            
            # Additional params for manual overrides (from admin or advanced users)
            model_type = data.get('model_type', 'best') 
            
            if not home_team or not away_team:
                return JsonResponse({'error': 'Home team and Away team are required'}, status=400)
            
            # Clean team names
            home_team = normalize_team_name(home_team)
            away_team = normalize_team_name(away_team)
            
            # Check for subscription/credits
            # For API usage, we might want to enforce stricter checks
            # This is a simplified check - production would use API keys
            if request.user.is_authenticated:
                user = request.user
                is_allowed = use_prediction_credit(user)
                if not is_allowed:
                    # Get detailed reason for failure
                    status = check_subscription_status(user)
                    message = status.get('message', 'Daily prediction limit reached. Please upgrade your plan.')
                    return JsonResponse({'error': message, 'code': 'LIMIT_REACHED'}, status=403)
            else:
                # Anonymous users are limited by session/IP (handled in views or middleware)
                pass

            # Load prediction models
            from .views import load_prediction_models
            model1, model2 = load_prediction_models()
            
            # Make prediction using advanced analytics
            result = advanced_predict_match(home_team, away_team, model1=model1, model2=model2)
            
            if not result:
                return JsonResponse({'error': 'Prediction failed - could not process teams'}, status=500)
            
            # Process result for JSON response
            # Convert any numpy types to python native types
            response_data = {
                'home_team': result.get('home_team', home_team),
                'away_team': result.get('away_team', away_team),
                'prediction': result.get('outcome', 'Draw'),
                'home_score': result.get('home_score', 0),
                'away_score': result.get('away_score', 0),
                'confidence': float(result.get('confidence', 0.5)),
                'probabilities': {
                    'Home': float(result.get('probabilities', {}).get(2, 0.33)),
                    'Draw': float(result.get('probabilities', {}).get(1, 0.33)),
                    'Away': float(result.get('probabilities', {}).get(0, 0.33))
                },
                'model_used': result.get('model_type', 'Unknown'),
                'analysis': result.get('final_prediction_text', result.get('outcome', 'Analysis complete'))
            }
            
            # Save prediction to DB is handled inside advanced_predict_match or we do it here?
            # Currently advanced_predict_match calculates but views.py saves...
            # The original logic in views.result saves it. 
            # Let's save it here for API consistency
            
            # ... (Save logic would go here if not centralized) ...
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"API Predict Error: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_teams_by_category(request):
    """API endpoint to get teams filtered by category/league.
    
    Expects GET with query parameters:
        category: "League Name"
    Returns JSON list of teams.
    """
    if request.method == 'GET':
        category = request.GET.get('category')
        if not category:
            return JsonResponse({'error': 'Category parameter is required'}, status=400)
        
        try:
            # Use analytics engine or DB to get teams
            # The analytics engine now uses DB via get_leagues_from_db
            from .analytics import get_leagues_from_db
            leagues_structure = get_leagues_from_db()

            # Find the specific category/league
            teams = []
            
            # leagues_structure is: { 'Category': { 'League': [teams] } }
            # But the UI sends specific leagues as 'category' sometimes (e.g. "Premier League")
            # We need to search through the structure
            
            found = False
            
            # 1. Check if it's a top-level category (e.g. "European Leagues")
            if category in leagues_structure:
                # Return all teams in this category? Or just list of leagues?
                # Usually we want teams for a specific Select element
                # If they select "European Leagues", usually the UI then asks for "Premier League"
                # But if this is populating a "Teams" dropdown directly:
                all_teams = []
                for league_name, league_teams in leagues_structure[category].items():
                    all_teams.extend(league_teams)
                teams = sorted(list(set(all_teams)))
                found = True
            
            # 2. Check if it's a specific league name (e.g. "Premier League")
            if not found:
                for cat, leagues in leagues_structure.items():
                    if category in leagues:
                        teams = leagues[category]
                        found = True
                        break
            
            if not found:
                 # Fallback to database direct query if not found in cache structure
                try:
                    league_obj = League.objects.filter(name__iexact=category).first()
                    if league_obj:
                        teams = sorted([t.name for t in league_obj.teams.all()])
                    else:
                         return JsonResponse({'teams': []}) # Return empty if really not found
                except Exception as db_e:
                     logger.error(f"DB lookup failed: {db_e}")
                     return JsonResponse({'teams': []})

            return JsonResponse({'teams': teams})
            
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_team_stats(request):
    """API endpoint for real-time team statistics.
    
    Expects GET with query parameters:
        team: "<team name>"
    Returns JSON with team statistics.
    """
    if request.method == 'GET':
        try:
            team_name = request.GET.get('team')
            if not team_name:
                return JsonResponse({'error': 'Team parameter is required'}, status=400)
            
            # Get team form
            form_data = analytics_engine.get_team_form(team_name)
            
            # Get team strength
            home_strength = analytics_engine.calculate_team_strength(team_name, 'home')
            away_strength = analytics_engine.calculate_team_strength(team_name, 'away')
            
            # Get team injury/suspension data (Not available in this version)
            injuries = None
            
            # Calculate recent form percentage
            if form_data and form_data.get('recent_form'):
                form_points = {'W': 3, 'D': 1, 'L': 0}
                recent_points = sum(form_points[result] for result in form_data['recent_form'][:5])
                max_points = 15  # 5 matches * 3 points
                form_percentage = (recent_points / max_points) * 100
            else:
                form_percentage = 50.0  # Default neutral form
            
            # Helper for safe mean calculation
            def safe_mean(lst):
                 if not lst: return 0.0
                 return float(sum(lst) / len(lst))

            stats = {
                'team_name': team_name,
                'recent_form': form_data['recent_form'][:5] if form_data and form_data.get('recent_form') else [],
                'form_percentage': round(form_percentage, 1),
                'goals_scored_avg': 0.0, # detailed stats temporarily unavailable
                'goals_conceded_avg': 0.0,
                'possession_avg': 50.0,
                'shots_on_target_avg': 0.0,
                'clean_sheets': int(form_data['clean_sheets']) if form_data else 0,
                'points': int(form_data['points']) if form_data else 0,
                'home_strength': float(round(home_strength * 100, 1)),
                'away_strength': float(round(away_strength * 100, 1)),
                'injuries': {
                    'key_players_out': 0,
                    'total_players_out': 0,
                    'impact_score': 0,
                    'expected_return': 0
                }
            }
            
            return JsonResponse(stats)
            
        except Exception as e:
            return JsonResponse({'error': f'Error getting team stats: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_head_to_head(request):
    """API endpoint for head-to-head statistics.
    
    Expects GET with query parameters:
        team1: "<team name>"
        team2: "<team name>"
    Returns JSON with head-to-head statistics.
    """
    if request.method == 'GET':
        try:
            team1 = request.GET.get('team1')
            team2 = request.GET.get('team2')
            
            if not team1 or not team2:
                return JsonResponse({'error': 'Both team1 and team2 parameters are required'}, status=400)
            
            # H2H stats data provider temporarily unavailable
            return JsonResponse({'error': 'No head-to-head data available'}, status=404)
            
        except Exception as e:
            return JsonResponse({'error': f'Error getting head-to-head stats: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_market_odds(request):
    """API endpoint for market betting odds.
    
    Expects GET with query parameters:
        home_team: "<team name>"
        away_team: "<team name>"
    Returns JSON with betting odds.
    """
    if request.method == 'GET':
        try:
            home_team = request.GET.get('home_team')
            away_team = request.GET.get('away_team')
            
            if not home_team or not away_team:
                return JsonResponse({'error': 'Both home_team and away_team parameters are required'}, status=400)
            
            # Market odds data provider temporarily unavailable
            return JsonResponse({'error': 'No odds data available'}, status=404)
            
        except Exception as e:
            return JsonResponse({'error': f'Error getting market odds: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def multi_match_predictions_api(request):
    """API endpoint to get multiple match predictions for the slip view."""
    if request.method == 'GET':
        try:
            # Get latest predictions for the user
            recent_cutoff = timezone.now() - timezone.timedelta(hours=24)
            
            if request.user.is_authenticated:
                predictions_qs = Prediction.objects.filter(
                    user=request.user,
                    is_archived=False,
                    prediction_date__gte=recent_cutoff
                ).order_by('-prediction_date')
            else:
                # Use session key for anonymous users
                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key
                predictions_qs = Prediction.objects.filter(
                    session_key=session_key,
                    is_archived=False,
                    prediction_date__gte=recent_cutoff
                ).order_by('-prediction_date')
            
            predictions_data = []
            for pred in predictions_qs:
                predictions_data.append({
                    'id': pred.id,
                    'home_team': pred.home_team,
                    'away_team': pred.away_team,
                    'outcome': pred.outcome,
                    'confidence': pred.confidence,
                    'prediction_date': pred.prediction_date.isoformat(),
                    'probabilities': {
                         'Home': pred.prob_home,
                         'Draw': pred.prob_draw,
                         'Away': pred.prob_away
                    }
                })
                
            return JsonResponse({'predictions': predictions_data})
        except Exception as e:
            logger.error(f"Error in multi-match API: {e}")
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
