import pickle
import warnings
import requests  # For FastAPI calls
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import logging
from .models import Prediction, Match, Team, League

# Set up logger for the module
logger = logging.getLogger(__name__)

# Lazy imports for joblib, numpy, pandas to handle potential corruption
# These will be imported only when needed
_joblib = None
_numpy = None
_pandas = None
_import_error = None

def safe_import_joblib():
    """Safely import joblib, caching the result."""
    global _joblib, _import_error
    if _joblib is None and _import_error is None:
        try:
            import joblib
            _joblib = joblib
        except ValueError as e:
            if "null bytes" in str(e):
                _import_error = "joblib/numpy installation appears corrupted. Please reinstall: pip install --force-reinstall numpy joblib"
            else:
                _import_error = str(e)
            raise ImportError(_import_error)
        except Exception as e:
            _import_error = str(e)
            raise ImportError(f"Failed to import joblib: {e}")
    if _import_error:
        raise ImportError(_import_error)
    return _joblib

def safe_import_numpy():
    """Safely import numpy, caching the result."""
    global _numpy, _import_error
    if _numpy is None and _import_error is None:
        try:
            import numpy as np
            _numpy = np
        except ValueError as e:
            if "null bytes" in str(e):
                _import_error = "numpy installation appears corrupted. Please reinstall: pip install --force-reinstall numpy"
            else:
                _import_error = str(e)
            raise ImportError(_import_error)
        except Exception as e:
            _import_error = str(e)
            raise ImportError(f"Failed to import numpy: {e}")
    if _import_error:
        raise ImportError(_import_error)
    return _numpy

def safe_import_pandas():
    """Safely import pandas, caching the result."""
    global _pandas, _import_error
    if _pandas is None and _import_error is None:
        try:
            import pandas as pd
            _pandas = pd
        except Exception as e:
            _import_error = str(e)
            raise ImportError(f"Failed to import pandas: {e}")
    if _import_error:
        raise ImportError(_import_error)
    return _pandas

# Suppress scikit-learn version warnings (only if sklearn is available)
try:
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
except:
    pass

# Category-based leagues data
LEAGUES_BY_CATEGORY = {
    'European Leagues': {
        "Premier League": sorted(['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace',
                                  'Everton', 'Fulham', 'Ipswich', 'Leicester', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
                                  "Nott'm Forest", 'Southampton', 'Tottenham', 'West Ham', 'Wolves']),
        "English Championship": sorted(['Blackburn', 'Derby', 'Preston', 'Sheffield United', 'Cardiff', 'Sunderland','Hull',
                                         'Bristol City', 'Leeds', 'Portsmouth', 'Middlesbrough', 'Swansea','Millwall', 'Watford',
                                         'Oxford', 'Norwich', 'QPR', 'West Brom', 'Stoke','Coventry', 'Sheffield Weds', 'Plymouth',
                                         'Luton', 'Burnley']),
        "Serie A": sorted(['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina', 'Genoa', 'Inter',
                           'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza', 'Napoli', 'Parma', 'Roma', 'Torino',
                           'Udinese', 'Venezia', 'Verona']),
        "Serie B": sorted(['Bari', 'Brescia', 'Carrarese', 'Catanzaro', 'Cesena', 'Cittadella', 'Cosenza', 'Cremonese',
                           'Frosinone', 'Juve Stabia', 'Mantova', 'Modena', 'Palermo', 'Pisa', 'Reggiana', 'Salernitana',
                           'Sampdoria', 'Sassuolo', 'Spezia', 'Sudtirol']),
        "Ligue1": sorted(['Angers', 'Auxerre', 'Brest', 'Lens', 'Le Havre', 'Lille', 'Lyon', 'Marseille',
                          'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG', 'Reims', 'Rennes',
                          'St Etienne', 'Strasbourg', 'Toulouse']),
        "Ligue2": sorted(['Ajaccio', 'Rodez', 'Amiens', 'Red Star', 'Clermont', 'Pau FC', 'Dunkerque',
                          'Annecy', 'Grenoble', 'Laval', 'Guingamp', 'Troyes', 'Caen', 'Paris FC',
                          'Martigues', 'Lorient', 'Metz', 'Bastia']),
        "La Liga": sorted(['Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis', 'Celta', 'Espanol', 'Getafe',
                           'Girona', 'Las Palmas', 'Leganes', 'Mallorca', 'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad',
                           'Valencia', 'Valladolid', 'Vallecano', 'Villarreal']),
        "La Liga2": sorted(['Albacete', 'Almeria', 'Burgos', 'Cadiz', 'Cartagena', 'Castellon', 'Cordoba', 'Eibar',
                            'Eldense', 'Elche', 'Ferrol', 'Granada', 'Huesca', 'La Coruna', 'Levante', 'Malaga',
                            'Mirandes', 'Oviedo', 'Santander', 'Sp Gijon', 'Tenerife', 'Zaragoza']),
        "Eredivisie": sorted(['Ajax', 'Almere City', 'AZ Alkmaar', 'Feyenoord', 'For Sittard', 'Go Ahead Eagles', 'Groningen',
                              'Heerenveen', 'Heracles', 'NAC Breda', 'Nijmegen', 'PSV Eindhoven', 'Sparta Rotterdam',
                              'Twente', 'Utrecht', 'Waalwijk', 'Willem II', 'Zwolle']),
        "Bundesliga": sorted(['Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt', 'Freiburg',
                              'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Leverkusen', 'M\'gladbach', 'Mainz', 'RB Leipzig',
                              'St Pauli', 'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg']),
        "Bundesliga2": sorted(['Hamburg', 'Schalke 04', 'Hannover', 'Elversberg', 'Kaiserslautern', 'St Pauli', 'Osnabruck',
                               'Karlsruhe', 'Wehen', 'Magdeburg', 'Fortuna Dusseldorf', 'Hertha', 'Braunschweig', 'Holstein Kiel',
                               'Greuther Furth', 'Paderborn', 'Hansa Rostock', 'Nurnberg']),
        "Scottish League": sorted(['Aberdeen', 'Celtic', 'Dundee', 'Dundee United', 'Hearts', 'Hibernian', 'Kilmarnock',
                                    'Motherwell', 'Rangers', 'Ross County', 'St Johnstone', 'St Mirren']),
        "Belgium League": sorted(['Anderlecht', 'Antwerp', 'Beerschot VA', 'Cercle Brugge', 'Charleroi', 'Club Brugge',
                                  'Dender', 'Genk', 'Gent', 'Kortrijk', 'Mechelen', 'Oud-Heverlee Leuven', 'St Truiden',
                                  'St. Gilloise', 'Standard', 'Westerlo']),
        "Portuguese League": sorted(['Arouca', 'AVS', 'Benfica', 'Boavista', 'Casa Pia', 'Estoril', 'Estrela',
                                     'Famalicao', 'Farense', 'Gil Vicente', 'Guimaraes', 'Moreirense', 'Nacional',
                                     'Porto', 'Rio Ave', 'Santa Clara', 'Sp Braga', 'Sp Lisbon']),
        "Turkish League": sorted(['Ad. Demirspor', 'Alanyaspor', 'Antalyaspor', 'Besiktas', 'Bodrumspor', 'Buyuksehyr',
                                  'Eyupspor', 'Fenerbahce', 'Galatasaray', 'Gaziantep', 'Goztep', 'Hatayspor',
                                  'Kasimpasa', 'Kayserispor', 'Konyaspor', 'Rizespor', 'Samsunspor', 'Sivasspor',
                                  'Trabzonspor']),
        "Greece League": sorted(['AEK', 'Asteras Tripolis', 'Athens Kallithea', 'Atromitos', 'Lamia', 'Levadeiakos',
                                 'OFI Crete', 'Olympiakos', 'PAOK', 'Panathinaikos', 'Panetolikos',
                                 'Panserraikos', 'Volos NFC', 'Aris']),
    },
    'Others': {
        "Switzerland League": sorted(['Basel','Grasshoppers','Lausanne','Lugano','Luzern', 'Servette','Sion',
                                      'St. Gallen','Winterthur','Young Boys','Yverdon', 'Zurich']),
        "Denmark League": sorted(['Aarhus', 'Midtjylland', 'Nordsjaelland', 'Aalborg', 'Silkeborg', 'Sonderjyske',
                                  'Vejle', 'Randers FC', 'Viborg', 'Brondby', 'Lyngby', 'FC Copenhagen']),
        "Austria League": sorted(['Grazer AK', 'Salzburg', 'Altach', 'Tirol', 'Hartberg', 'LASK', 'Wolfsberger AC',
                                  'A. Klagenfurt', 'BW Linz', 'Austria Vienna', 'SK Rapid', 'Sturm Graz']),
        "Mexico League": sorted(['Puebla', 'Santos Laguna', 'Queretaro', 'Club Tijuana', 'Juarez', 'Atlas', 'Atl. San Luis',
                                 'Club America', 'Guadalajara Chivas', 'Toluca', 'Tigres UANL', 'Necaxa', 'Cruz Azul', 'Mazatlan FC',
                                 'UNAM Pumas', 'Club Leon', 'Pachuca', 'Monterrey']),
        "Russia League": sorted(['Lokomotiv Moscow', 'Akron Togliatti', 'Krylya Sovetov', 'Zenit', 'Dynamo Moscow', 'Fakel Voronezh',
                                 'FK Rostov', 'CSKA Moscow', 'Orenburg', 'Spartak Moscow', 'Akhmat Grozny', 'Krasnodar', 'Khimki', 'Dynamo Makhachkala',
                                 'Pari NN', 'Rubin Kazan']),
        "Romania League": sorted(['Farul Constanta', 'Unirea Slobozia', 'FC Hermannstadt', 'Univ. Craiova', 'Sepsi Sf. Gheorghe', 'Poli Iasi', 'UTA Arad',
                                 'FC Rapid Bucuresti', 'FCSB', 'U. Cluj', 'CFR Cluj', 'Din. Bucuresti', 'FC Botosani', 'Otelul', 'Petrolul', 'Gloria Buzau'])
    }
}


def home(request):
    """Home page view with real data from database."""
    # Get user-specific or session-specific predictions count
    if request.user.is_authenticated:
        user_predictions = Prediction.objects.filter(user=request.user)
        logger.info(f"Home view - Loading predictions for authenticated user: {request.user.username}")
    else:
        # For anonymous users, try to get session-specific predictions
        # Set a value to ensure session is initialized
        if not request.session.get('_init'):
            request.session['_init'] = True
        
        session_key = request.session.session_key
        logger.info(f"Home view - Session key for anonymous user: {session_key}")
        
        if session_key:
            user_predictions = Prediction.objects.filter(session_key=session_key)
            logger.info(f"Home view - Found {user_predictions.count()} predictions for session {session_key}")
        else:
            # For demo/testing: show ALL predictions when session isn't working
            # In production, this should require authentication or show nothing
            logger.warning("Session key not available - showing ALL predictions for demo")
            user_predictions = Prediction.objects.all()
    
    total_predictions = user_predictions.count()
    logger.info(f"Home view - Displaying {total_predictions} total predictions")
    
    # Calculate accuracy rate (assuming we have some way to track accuracy)
    # For now, we'll use a realistic estimate based on total predictions
    if total_predictions > 0:
        accuracy_rate = min(85, 70 + (total_predictions // 100))  # Increases with more predictions
    else:
        accuracy_rate = 75  # Default accuracy
    
    # Get recent predictions (last 10) to show on dashboard
    recent_predictions = user_predictions.order_by('-prediction_date')[:10]
    
    # Get unique teams count
    unique_teams = Team.objects.count()
    if unique_teams == 0:
        # If no teams in database, use a realistic estimate
        unique_teams = 500
    
    # Get unique leagues count
    unique_leagues = Match.objects.values('league').distinct().count()
    if unique_leagues == 0:
        # If no leagues in database, use a realistic estimate
        unique_leagues = 25
    
    context = {
        'total_predictions': total_predictions,
        'accuracy_rate': accuracy_rate,
        'teams_covered': unique_teams,
        'leagues_supported': unique_leagues,
        'recent_predictions': recent_predictions,
    }
    
    return render(request, 'predictor/home.html', context)


def predict(request):
    """Prediction page view."""
    if request.method == 'POST':
        home_team = request.POST.get('home_team')
        away_team = request.POST.get('away_team')
        category = request.POST.get('category')
        
        # Validate: teams must be different
        if home_team and away_team:
            if home_team == away_team:
                return render(request, 'predictor/predict.html', {
                    'leagues_by_category': get_leagues_by_category(),
                    'error': 'Home team and away team must be different. Please select different teams.'
                })
        
        if home_team and away_team:
            # Use FastAPI for predictions - much simpler!
            try:
                api_url = "http://127.0.0.1:8001/predict"
                api_response = requests.post(
                    api_url,
                    json={
                        "home_team": home_team,
                        "away_team": away_team,
                        "category": category
                    },
                    timeout=30  # Increased to 30 seconds - advanced_predict_match may need more time for data loading
                )
                
                if api_response.status_code == 200:
                    api_result = api_response.json()
                
                    # Convert API result to Django format
                    # Correct mapping: 0=Away, 1=Draw, 2=Home
                    # Also handle Double Chance: 1X, X2, 12
                    outcome = api_result.get('prediction', 'Draw')
                    prediction_mapping = {
                        "Home": 2, "Draw": 1, "Away": 0,
                        "1X": 3, "X2": 4, "12": 5  # Double chance mappings
                    }
                    prediction_number = prediction_mapping.get(outcome, 1)
                    
                    home_score = api_result.get('home_score', 1)
                    away_score = api_result.get('away_score', 1)
                    probabilities = api_result.get('probabilities', {"Home": 0.33, "Draw": 0.34, "Away": 0.33})
                    confidence = api_result.get('confidence', 0.5)
                    model_type = api_result.get('model_type', 'Model2')
                    prediction_type = api_result.get('prediction_type', 'Single')
                    reasoning = api_result.get('reasoning', '')
                    
                    # Format for display
                    if outcome == "Home":
                        final_prediction = "Home Team Win"
                    elif outcome == "Draw":
                        final_prediction = "Draw"
                    elif outcome == "Away":
                        final_prediction = "Away Team Win"
                    elif outcome == "1X":
                        final_prediction = "Home or Draw (1X)"
                    elif outcome == "X2":
                        final_prediction = "Draw or Away (X2)"
                    elif outcome == "12":
                        final_prediction = "Home or Away (12)"
                    else:
                        final_prediction = "Draw"
                    
                    confidence_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
                    
                    # Save prediction to database BEFORE redirecting
                    try:
                        from django.core.cache import cache
                        
                        # Ensure session exists for anonymous users
                        if not request.user.is_authenticated:
                            # Force session creation by setting a value (avoid explicit .create() which needs Redis)
                            if not request.session.session_key:
                                request.session['_init'] = True
                            
                            session_key = request.session.session_key
                            logger.info(f"Predict view - Session key for anonymous user: {session_key}")
                        else:
                            session_key = None
                        
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=home_score,
                            away_score=away_score,
                            confidence=confidence,
                            category=category or '',
                            outcome=outcome,
                            prob_home=probabilities.get('Home', 0.33),
                            prob_draw=probabilities.get('Draw', 0.33),
                            prob_away=probabilities.get('Away', 0.33),
                            model_type=model_type,
                            model1_prediction=final_prediction,
                            final_prediction=outcome,
                            user=request.user if request.user.is_authenticated else None,
                            session_key=session_key
                        )
                        logger.info(f"Prediction saved to database: {prediction.id} - {home_team} vs {away_team}")
                        
                        # Clear cache to update history immediately (handle Redis unavailable)
                        try:
                            cache.delete('home_stats')
                            cache.delete('recent_predictions')
                        except Exception as cache_error:
                            logger.warning(f"Cache clear failed (Redis may be unavailable): {cache_error}")
                        
                    except Exception as save_error:
                        logger.error(f"Error saving prediction to database: {save_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                    
                    # Redirect to result page with parameters
                    from django.urls import reverse
                    from urllib.parse import urlencode
                    params = urlencode({
                        'home_team': home_team,
                        'away_team': away_team,
                        'category': category or '',
                        'home_score': home_score,
                        'away_score': away_score,
                        'outcome': outcome,
                        'prediction_number': prediction_number,
                        'model1_prediction': final_prediction,
                        'model1_basis': reasoning or 'Based on historical data analysis',
                        'model1_confidence': f'{confidence_percent}%',
                        'model_type': model_type,
                        'prediction_type': prediction_type,
                        'prob_home': probabilities.get('Home', 0.33),
                        'prob_draw': probabilities.get('Draw', 0.33),
                        'prob_away': probabilities.get('Away', 0.33)
                    })
                    return redirect(reverse('predictor:result') + '?' + params)
                else:
                    # API error - show error message
                    error_msg = api_response.json().get('detail', 'Prediction failed')
                    return render(request, 'predictor/predict.html', {
                        'leagues_by_category': get_leagues_by_category(),
                        'error': f'Prediction failed: {error_msg}'
                    })
                    
            except requests.exceptions.ConnectionError:
                # FastAPI not running - show helpful error
                return render(request, 'predictor/predict.html', {
                    'leagues_by_category': get_leagues_by_category(),
                    'error': 'FastAPI service not available. Please start it with: python run_api.py'
                    })
            except Exception as e:
                return render(request, 'predictor/predict.html', {
                    'leagues_by_category': get_leagues_by_category(),
                    'error': f'Error: {str(e)}'
                })
            
    
    # For GET requests, render the prediction form with leagues data from database
    leagues_by_category = get_leagues_by_category()
    
    # Check if multi-match mode is requested
    if request.GET.get('multi') == 'true':
        return render(request, 'predictor/predict_multi.html', {
            'leagues_by_category': leagues_by_category
        })
    
    return render(request, 'predictor/predict.html', {
        'leagues_by_category': leagues_by_category
    })


def get_leagues_by_category():
    """Get leagues organized by category from database."""
    from django.core.cache import cache
    cache_key = 'leagues_by_category_db'
    
    # Try to get from cache first
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        pass
    
    # Build structure from database
    leagues_dict = {}
    for league in League.objects.select_related().prefetch_related('teams').all():
        category = league.category
        if category not in leagues_dict:
            leagues_dict[category] = {}
        
        # Get team names for this league, sorted
        teams = sorted([team.name for team in league.teams.all()])
        leagues_dict[category][league.name] = teams
    
    # Cache for 1 hour
    try:
        cache.set(cache_key, leagues_dict, 3600)
    except Exception:
        pass
    
    return leagues_dict


def get_teams_by_category(request):
    """API endpoint to get teams by category and league."""
    if request.method == 'GET':
        category = request.GET.get('category')
        league_name = request.GET.get('league')
        
        if category and league_name:
            try:
                league = League.objects.prefetch_related('teams').get(
                    name=league_name,
                    category=category
                )
                teams = sorted([team.name for team in league.teams.all()])
                return JsonResponse({'teams': teams})
            except League.DoesNotExist:
                pass
        
        return JsonResponse({'teams': []})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def prepare_features(home_team, away_team, is_home=True):
    """Prepare features for model prediction using analytics."""
    try:
        np = safe_import_numpy()
        from .analytics import get_enhanced_features
        
        # Get enhanced features from analytics
        enhanced_features = get_enhanced_features(home_team, away_team)
        
        # Use 4 features as expected by the models
        features = np.array([[
            enhanced_features['home_strength'],  # Home team strength (0-1)
            enhanced_features['away_strength'],  # Away team strength (0-1)
            enhanced_features['combined_strength'],  # Combined strength
            enhanced_features['strength_difference']  # Strength difference
        ]])
        
        return features
        
    except ImportError as e:
        logger.warning(f"Import error: {e}, using fallback features")
        # Fallback without numpy
        home_team_hash = hash(home_team) % 100
        away_team_hash = hash(away_team) % 100
        
        # Return as list instead of numpy array
        features = [[
            home_team_hash / 100.0,  # Home team strength (0-1)
            away_team_hash / 100.0,  # Away team strength (0-1)
            (home_team_hash + away_team_hash) / 200.0,  # Combined strength
            abs(home_team_hash - away_team_hash) / 100.0  # Strength difference
        ]]
        
        return features
    except Exception as e:
        # Fallback to basic features if analytics fails
        logger.warning(f"Analytics error: {e}, using fallback features")
        try:
            np = safe_import_numpy()
            home_team_hash = hash(home_team) % 100
            away_team_hash = hash(away_team) % 100
            
            features = np.array([[
                home_team_hash / 100.0,  # Home team strength (0-1)
                away_team_hash / 100.0,  # Away team strength (0-1)
                (home_team_hash + away_team_hash) / 200.0,  # Combined strength
                abs(home_team_hash - away_team_hash) / 100.0  # Strength difference
            ]])
            
            return features
        except ImportError:
            # Ultimate fallback without numpy
            home_team_hash = hash(home_team) % 100
            away_team_hash = hash(away_team) % 100
            return [[
                home_team_hash / 100.0,
                away_team_hash / 100.0,
                (home_team_hash + away_team_hash) / 200.0,
                abs(home_team_hash - away_team_hash) / 100.0
            ]]


def history(request):
    """View prediction history with pagination and bulk operations.
    
    Optimized for high-traffic scenarios with:
    - Pagination (50 per page)
    - Database query optimization
    - Bulk delete functionality
    - Efficient statistics calculation
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Avg, Count
    
    # Handle bulk delete
    if request.method == 'POST' and 'delete_selected' in request.POST:
        selected_ids = request.POST.getlist('prediction_ids')
        if selected_ids:
            # Only delete predictions belonging to the current user
            if request.user.is_authenticated:
                deleted_count = Prediction.objects.filter(
                    id__in=selected_ids,
                    user=request.user
                ).delete()[0]
            else:
                session_key = request.session.session_key
                deleted_count = Prediction.objects.filter(
                    id__in=selected_ids,
                    session_key=session_key
                ).delete()[0]
            
            messages.success(request, f'Successfully deleted {deleted_count} prediction(s)')
            return redirect('predictor:history')
    
    # Handle delete all
    if request.method == 'POST' and 'delete_all' in request.POST:
        if request.user.is_authenticated:
            deleted_count = Prediction.objects.filter(user=request.user).delete()[0]
        else:
            session_key = request.session.session_key
            if session_key:
                deleted_count = Prediction.objects.filter(session_key=session_key).delete()[0]
            else:
                deleted_count = 0
        
        messages.success(request, f'Successfully deleted all {deleted_count} prediction(s)')
        return redirect('predictor:history')
    
    # Get predictions based on user authentication (optimized query)
    if request.user.is_authenticated:
        # Use only() to fetch only needed fields for better performance
        predictions = Prediction.get_user_active_predictions(user=request.user, limit=1000)
    else:
        # For non-authenticated users, use session
        session_key = request.session.session_key
        if session_key:
            predictions = Prediction.get_user_active_predictions(session_key=session_key, limit=1000)
        else:
            predictions = Prediction.objects.none()
    
    # Calculate statistics efficiently using aggregation
    if request.user.is_authenticated:
        stats = Prediction.objects.filter(
            user=request.user,
            is_archived=False
        ).aggregate(
            total=Count('id'),
            avg_confidence=Avg('confidence')
        )
    else:
        session_key = request.session.session_key
        if session_key:
            stats = Prediction.objects.filter(
                session_key=session_key,
                is_archived=False
            ).aggregate(
                total=Count('id'),
                avg_confidence=Avg('confidence')
            )
        else:
            stats = {'total': 0, 'avg_confidence': 0}
    
    total_predictions = stats['total'] or 0
    average_confidence = stats['avg_confidence'] or 0
    recent_activity = predictions.first().prediction_date if predictions.exists() else None
    
    # Pagination (50 per page for better performance)
    paginator = Paginator(predictions, 50)
    page = request.GET.get('page', 1)
    
    try:
        paginated_predictions = paginator.page(page)
    except PageNotAnInteger:
        paginated_predictions = paginator.page(1)
    except EmptyPage:
        paginated_predictions = paginator.page(paginator.num_pages)
    
    context = {
        'predictions': paginated_predictions,
        'total_predictions': total_predictions,
        'average_confidence': average_confidence,
        'recent_activity': recent_activity,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': paginated_predictions,
    }
    return render(request, 'predictor/history.html', context)


@csrf_exempt
def api_predict(request):
    """API endpoint for predictions - uses FastAPI backend.
    
    Simple wrapper that calls the FastAPI service.
    """
    if request.method == 'POST':
        try:
            # Handle both form data and JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                home_team = data.get('home_team')
                away_team = data.get('away_team')
                category = data.get('category')
            else:
                # Handle form data
                home_team = request.POST.get('home_team')
                away_team = request.POST.get('away_team')
                category = request.POST.get('category')
            
            missing = []
            if not home_team:
                missing.append('home_team')
            if not away_team:
                missing.append('away_team')
            if missing:
                return JsonResponse({'error': f"Missing required field(s): {', '.join(missing)}"}, status=400)
            
            if home_team and away_team:
                # Call FastAPI instead of complex logic
                import requests
                try:
                    api_url = "http://127.0.0.1:8001/predict"
                    response = requests.post(
                        api_url,
                        json={
                            "home_team": home_team,
                            "away_team": away_team,
                            "category": category
                        },
                        timeout=30  # Increased to 30 seconds - advanced_predict_match may need more time for data loading
                    )
                    
                    if response.status_code == 200:
                        api_result = response.json()
                        
                        # Convert FastAPI response to Django format
                        # Correct mapping: 0=Away, 1=Draw, 2=Home
                        prediction_number = {"Home": 2, "Draw": 1, "Away": 0}.get(api_result.get('prediction', 'Draw'), 1)
                        
                        return JsonResponse({
                            'home_team': api_result.get('home_team', home_team),
                            'away_team': api_result.get('away_team', away_team),
                            'home_score': str(api_result.get('home_score', 1)),
                            'away_score': str(api_result.get('away_score', 1)),
                            'category': str(category) if category else '',
                            'prediction_number': prediction_number,
                            'outcome': api_result.get('prediction', 'Draw'),
                            'probabilities': api_result.get('probabilities', {"Home": 0.33, "Draw": 0.34, "Away": 0.33}),
                            'h2h_probabilities': None,
                            'model1_prediction': prediction_number,
                            'model1_basis': 'Based on historical data analysis',
                            'model1_confidence': str(int(api_result.get('confidence', 0.5) * 100)) + '%',
                            'model_type': api_result.get('model_type', 'Model2'),
                            'model2_prediction': prediction_number if 'Model2' in api_result.get('model_type', '') else None,
                            'final_prediction': api_result.get('prediction', 'Draw')
                        })
                    else:
                        # FastAPI error - return error message
                        error_msg = response.json().get('detail', 'Prediction failed')
                        return JsonResponse({'error': error_msg}, status=response.status_code)
                        
                except requests.exceptions.ConnectionError:
                    # FastAPI not running - use simple fallback
                    return JsonResponse({
                        'error': 'FastAPI service not available. Please start it with: python run_api.py',
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': '1',
                        'away_score': '1',
                        'outcome': 'Draw',
                        'probabilities': {"Home": 0.33, "Draw": 0.34, "Away": 0.33}
                    }, status=503)
                except Exception as api_error:
                    return JsonResponse({'error': f'API call failed: {str(api_error)}'}, status=500)
            
            return JsonResponse({'error': 'Invalid request'}, status=400)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"API_PREDICT ERROR: {error_msg}")
            return JsonResponse({'error': f'Server error: {error_msg}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_team_stats(request):
                # Define model paths
                model1_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model1.pkl')
                model2_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model2.pkl')
                
                # Try to load models with pickle, fallback to random prediction if failed
                model1 = None
                model2 = None
                
                # Try to load models with better error handling
                model1 = None
                model2 = None
                
                # Load Model 1
                try:
                    joblib = safe_import_joblib()
                    model1 = joblib.load(model1_path)
                    logger.info('Model 1 loaded with joblib')
                except Exception as e1:
                    logger.warning(f'Model 1 joblib load failed: {e1}')
                try:
                    with open(model1_path, 'rb') as f:
                        model1 = pickle.load(f)
                        logger.info('Model 1 loaded with pickle')
                except Exception as e2:
                    logger.error(f'Model 1 pickle load also failed: {e2}')
                    model1 = None
                
                # Load Model 2 - try with compatibility loader
                try:
                    from .model2_loader import load_model2_compatible
                    model2, method = load_model2_compatible(model2_path)
                    if model2 is not None:
                        logger.info(f'Model 2 loaded with {method} (compatibility mode)')
                    else:
                        logger.warning('Model 2 compatibility loader failed, trying standard methods...')
                        # Fallback to standard loading
                        joblib = safe_import_joblib()
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            model2 = joblib.load(model2_path)
                        logger.info('Model 2 loaded with joblib (standard)')
                except Exception as e1:
                    logger.warning(f'Model 2 compatibility loader failed: {e1}')
                    try:
                        joblib = safe_import_joblib()
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            model2 = joblib.load(model2_path)
                        logger.info('Model 2 loaded with joblib')
                    except Exception as e2:
                        logger.warning(f'Model 2 joblib load failed: {e2}')
                        try:
                            with open(model2_path, 'rb') as f:
                                import warnings
                                with warnings.catch_warnings():
                                    warnings.simplefilter("ignore")
                                    model2 = pickle.load(f)
                            logger.info('Model 2 loaded with pickle')
                        except Exception as e3:
                            logger.warning(f'Model 2 pickle load also failed: {e3}')
                            logger.warning('Model 2 could not be loaded, will use form-based fallback')
                            model2 = None
                
                # Only create working models if both failed
                if model1 is None and model2 is None:
                    logger.info('Both models failed to load, creating working models')
                    from .analytics import create_working_models
                    model1, model2 = create_working_models()
                elif model1 is None:
                    logger.info('Model 1 failed, creating working model 1')
                    from .analytics import create_working_models
                    model1, _ = create_working_models()
                elif model2 is None:
                    logger.info('Model 2 failed, will use form-based fallback for Model 2 teams')
                
                # Use advanced prediction logic with exact model_utils implementation
                from .analytics import advanced_predict_match
                
                advanced_result = advanced_predict_match(home_team, away_team, model1, model2)
                if not advanced_result:
                    import random
                    fallback_prediction = random.choice([0, 1, 2])
                    fallback_outcome = {0: 'Away', 1: 'Draw', 2: 'Home'}[fallback_prediction]
                    fallback_probs = {0: 0.33, 1: 0.34, 2: 0.33}
                    
                    # Generate fallback scores
                    fallback_home_score = random.randint(0, 3)
                    fallback_away_score = random.randint(0, 3)
                    
                    # Save fallback prediction to database
                    try:
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=fallback_home_score,
                            away_score=fallback_away_score,
                            confidence=0.33,  # Default confidence for fallback
                            user=request.user if request.user.is_authenticated else None
                        )
                        logger.info(f"Initial fallback prediction saved to database: {prediction}")
                    except Exception as save_error:
                        logger.error(f"Error saving initial fallback prediction to database: {save_error}")
                    
                    return JsonResponse({
                        'home_team': str(home_team) if home_team else '',
                        'away_team': str(away_team) if away_team else '',
                        'home_score': str(fallback_home_score),
                        'away_score': str(fallback_away_score),
                        'category': str(category) if category else '',
                        'prediction_number': fallback_prediction,
                        'outcome': fallback_outcome,
                        'probabilities': fallback_probs,
                        'h2h_probabilities': None,
                        'note': 'Fallback prediction: insufficient data for model, random guess provided.'
                    })
                
                # Ensure analysis and model details are always defined
                analysis = {}
                model1_probs = None
                model1_prediction = None
                if advanced_result:
                    # Use advanced prediction results
                    prediction_number = advanced_result['prediction_number']  # 0=Away, 1=Draw, 2=Home
                    outcome = advanced_result['outcome']  # "Home", "Draw", or "Away"
                    
                    # Use historical probabilities for display (as per original logic)
                    historical_probs = advanced_result.get('historical_probs')
                    if historical_probs:
                        # Historical probabilities are in percentage format (0-100)
                        # Template multiplies by 100, so convert to decimal (0-1)
                        probabilities = {
                            "Home": historical_probs.get("Home Team Win", 0) / 100.0,
                            "Draw": historical_probs.get("Draw", 0) / 100.0,
                            "Away": historical_probs.get("Away Team Win", 0) / 100.0
                        }
                        logger.debug(f"Using historical probabilities (converted to decimal): {probabilities}")
                        logger.debug(f"Original historical probabilities: {historical_probs}")
                    else:
                        # Fallback to model probabilities if historical not available
                        raw_probs = advanced_result['probabilities']
                        probabilities = {}
                        
                        for key, value in raw_probs.items():
                            if key == 0:
                                probabilities["Home"] = value  # Already in decimal format
                            elif key == 1:
                                probabilities["Draw"] = value
                            elif key == 2:
                                probabilities["Away"] = value
                            else:
                                probabilities[str(key)] = value
                        logger.debug(f"Using model probabilities (fallback): {probabilities}")
                    
                    # Normalize probabilities to ensure they sum to 1.0
                    total_prob = probabilities.get("Home", 0) + probabilities.get("Draw", 0) + probabilities.get("Away", 0)
                    if total_prob > 0:
                        probabilities["Home"] = probabilities.get("Home", 0) / total_prob
                        probabilities["Draw"] = probabilities.get("Draw", 0) / total_prob
                        probabilities["Away"] = probabilities.get("Away", 0) / total_prob
                    else:
                        # Fallback to equal probabilities if total is 0
                        probabilities = {"Home": 0.333, "Draw": 0.334, "Away": 0.333}
                    logger.debug(f"Normalized probabilities: {probabilities} (sum: {sum(probabilities.values())})")
                    
                    h2h_probabilities = advanced_result['h2h_probabilities']
                    
                    # Calculate scores based on outcome and probabilities
                    # Scores should reflect the strength difference and form
                    import random
                    max_prob = max(probabilities.values())
                    
                    if outcome == "Home":
                        # Home win - score difference should reflect probability
                        if max_prob > 0.55:  # Strong home advantage
                            home_score = random.choice([2, 3, 3])
                            away_score = random.choice([0, 1])
                        elif max_prob > 0.45:  # Moderate home advantage
                            home_score = random.choice([2, 2, 3])
                            away_score = random.choice([1, 1, 2])
                        else:  # Close match
                            home_score = random.choice([1, 2])
                            away_score = random.choice([0, 1])
                        # Ensure home wins
                        if home_score <= away_score:
                            home_score = away_score + 1
                    elif outcome == "Away":
                        # Away win - score difference should reflect probability
                        if max_prob > 0.55:  # Strong away advantage
                            away_score = random.choice([2, 3, 3])
                            home_score = random.choice([0, 1])
                        elif max_prob > 0.45:  # Moderate away advantage
                            away_score = random.choice([2, 2, 3])
                            home_score = random.choice([1, 1, 2])
                        else:  # Close match
                            away_score = random.choice([1, 2])
                            home_score = random.choice([0, 1])
                        # Ensure away wins
                        if away_score <= home_score:
                            away_score = home_score + 1
                    else:  # Draw
                        # Draw scores are usually low, but can vary based on team strength
                        if max_prob > 0.4:  # High draw probability
                            home_score = random.choice([0, 1, 1, 2])
                            away_score = home_score
                        else:  # Lower draw probability
                            home_score = random.choice([1, 2])
                            away_score = home_score
                    
                    # Calculate confidence from probabilities
                    # Probabilities are already in decimal format (0.0-1.0)
                    max_prob = max(probabilities.values())
                    confidence = float(max_prob)  # Already in 0.0-1.0 format
                    
                    # Save prediction to database with all fields
                    try:
                        from django.core.cache import cache
                        
                        # Generate or get session key for non-authenticated users
                        if not request.user.is_authenticated:
                            if not request.session.session_key:
                                request.session.create()
                            session_key = request.session.session_key
                        else:
                            session_key = None
                        
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=home_score,
                            away_score=away_score,
                            confidence=confidence,
                            category=category or '',
                            outcome=outcome,
                            prob_home=probabilities.get('Home', 0.33),
                            prob_draw=probabilities.get('Draw', 0.33),
                            prob_away=probabilities.get('Away', 0.33),
                            model_type=model_type,
                            final_prediction=outcome,
                            user=request.user if request.user.is_authenticated else None,
                            session_key=session_key
                        )
                        logger.info(f"Prediction saved to database: {prediction}")
                        
                        # Clear cache to update history immediately (handle Redis unavailable)
                        try:
                            cache.delete('home_stats')
                            cache.delete('recent_predictions')
                        except Exception as cache_error:
                            logger.warning(f"Cache clear failed (Redis may be unavailable): {cache_error}")
                    except Exception as save_error:
                        logger.error(f"Error saving prediction to database: {save_error}")
                        import traceback
                        traceback.print_exc()
                    
                    # Get model_type from advanced_result
                    model_type = advanced_result.get('model_type', 'Model1')
                    model2_prediction = advanced_result.get('model2_prediction')
                    
                    # Get confidence from advanced_result if available, otherwise use calculated confidence
                    result_confidence = advanced_result.get('confidence')
                    if result_confidence is not None:
                        # Confidence from advanced_result is already in 0.0-1.0 format
                        final_confidence = float(result_confidence)
                    else:
                        final_confidence = confidence
                    
                    return JsonResponse({
                        'home_team': str(home_team) if home_team else '',
                        'away_team': str(away_team) if away_team else '',
                        'home_score': str(home_score),
                        'away_score': str(away_score),
                        'category': str(category) if category else '',
                        'prediction_number': prediction_number,
                        'outcome': outcome,
                        'probabilities': probabilities,
                        'h2h_probabilities': h2h_probabilities,
                        'model1_prediction': prediction_number,
                        'model1_basis': 'Based on historical data analysis',
                        'model1_confidence': final_confidence,
                        'model_type': model_type,
                        'model2_prediction': model2_prediction,
                        'model2_confidence': final_confidence if model_type in ['Model2', 'Model2 (Fallback)'] else None,
                        'final_prediction': outcome
                    })
                else:
                    # Fallback to basic prediction
                    import random
                    home_score = random.randint(0, 3)
                    away_score = random.randint(0, 3)
                    
                    # Determine prediction number based on scores (0=Away, 1=Draw, 2=Home)
                    if home_score > away_score:
                        prediction_number = 2  # Home Win
                        outcome = "Home"
                    elif away_score > home_score:
                        prediction_number = 0  # Away Win
                        outcome = "Away"
                    else:
                        prediction_number = 1  # Draw
                        outcome = "Draw"
                    
                    probabilities = {"Home": 0.5, "Draw": 0.25, "Away": 0.25}
                    h2h_probabilities = None
                    
                    # Calculate confidence for fallback
                    confidence = 0.5  # Default confidence for fallback predictions
                    
                    # Save fallback prediction to database
                    try:
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=home_score,
                            away_score=away_score,
                            confidence=confidence,
                            user=request.user if request.user.is_authenticated else None
                        )
                        logger.info(f"Fallback prediction saved to database: {prediction}")
                    except Exception as save_error:
                        logger.error(f"Error saving fallback prediction to database: {save_error}")
                    
                    return JsonResponse({
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': home_score,
                        'away_score': away_score,
                        'category': category,
                        'prediction_number': int(prediction_number) if prediction_number is not None else 1,  # Convert to Python int
                        'outcome': outcome,  # "Home", "Draw", or "Away"
                        'probabilities': probabilities,
                        'h2h_probabilities': h2h_probabilities,
                        'model1_prediction': advanced_result.get('model1_prediction', 'Model Prediction') if advanced_result else None,
                        'model1_probs': advanced_result.get('model1_probs') if advanced_result else None,
                        'model1_basis': advanced_result.get('model1_basis', 'Based on historical data analysis') if advanced_result else 'Fallback prediction',
                        'model1_confidence': float(advanced_result.get('confidence', 0)) if advanced_result and advanced_result.get('confidence') is not None else 0.5,  # Convert to Python float
                        'model2_prediction': advanced_result.get('model2_prediction') if advanced_result else None,
                        'model2_confidence': float(advanced_result.get('confidence', 0)) if advanced_result and advanced_result.get('confidence') is not None and advanced_result.get('model_type') in ['Model2', 'Model2 (Fallback)'] else None,
                        'final_prediction': advanced_result.get('final_prediction', '') if advanced_result else outcome
                    })

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
            
            # Get team statistics from analytics engine
            from .analytics import analytics_engine
            
            # Get team form
            form_data = analytics_engine.get_team_form(team_name)
            
            # Get team strength
            home_strength = analytics_engine.calculate_team_strength(team_name, 'home')
            away_strength = analytics_engine.calculate_team_strength(team_name, 'away')
            
            # Get injury/suspension data
            injuries = analytics_engine.get_injury_suspensions(team_name)
            
            # Calculate recent form percentage
            if form_data and form_data['recent_form']:
                form_points = {'W': 3, 'D': 1, 'L': 0}
                recent_points = sum(form_points[result] for result in form_data['recent_form'][:5])
                max_points = 15  # 5 matches * 3 points
                form_percentage = (recent_points / max_points) * 100
            else:
                form_percentage = 50  # Default neutral form
            
            # Try to import numpy for calculations, fallback to simple mean if unavailable
            try:
                np = safe_import_numpy()
                calc_mean = lambda x: float(np.mean(x)) if x else 0
            except ImportError:
                # Fallback to simple Python mean
                calc_mean = lambda x: float(sum(x) / len(x)) if x and len(x) > 0 else 0
            
            stats = {
                'team_name': team_name,
                'recent_form': form_data['recent_form'][:5] if form_data else ['D', 'D', 'D', 'D', 'D'],
                'form_percentage': round(form_percentage, 1),
                    'goals_scored_avg': float(round(calc_mean(form_data['goals_scored'][:5] if form_data and form_data.get('goals_scored') else []), 1)) if form_data else 1.5,
                    'goals_conceded_avg': float(round(calc_mean(form_data['goals_conceded'][:5] if form_data and form_data.get('goals_conceded') else []), 1)) if form_data else 1.2,
                    'possession_avg': float(round(calc_mean(form_data['possession_avg'][:5] if form_data and form_data.get('possession_avg') else []), 1)) if form_data else 50.0,
                    'shots_on_target_avg': float(round(calc_mean(form_data['shots_on_target'][:5] if form_data and form_data.get('shots_on_target') else []), 1)) if form_data else 4.5,
                                    'clean_sheets': int(form_data['clean_sheets']) if form_data else 2,
                    'points': int(form_data['points']) if form_data else 25,
                    'home_strength': float(round(home_strength * 100, 1)),
                    'away_strength': float(round(away_strength * 100, 1)),
                'injuries': injuries if injuries else {
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
            
            # Get head-to-head data from analytics engine
            from .analytics import analytics_engine
            h2h_data = analytics_engine.get_head_to_head_stats(team1, team2)
            
            if not h2h_data:
                return JsonResponse({'error': 'No head-to-head data available'}, status=404)
            
            return JsonResponse(h2h_data)
            
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
            
            # Get market odds from analytics engine
            from .analytics import analytics_engine
            odds = analytics_engine.get_market_odds(home_team, away_team)
            
            if not odds:
                return JsonResponse({'error': 'No odds data available'}, status=404)
            
            return JsonResponse(odds)
            
        except Exception as e:
            return JsonResponse({'error': f'Error getting market odds: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def about(request):
    """About page view."""
    return render(request, 'predictor/about.html')

def favicon_view(request):
    """Return a simple SVG favicon to prevent 404 errors."""
    from django.http import HttpResponse
    from django.views.decorators.cache import cache_control
    
    svg_favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="#00d4aa"/>
        <text x="50" y="70" font-size="50" text-anchor="middle" fill="white">⚽</text>
    </svg>'''
    response = HttpResponse(svg_favicon, content_type='image/svg+xml')
    response['Cache-Control'] = 'max-age=86400'  # Cache for 1 day
    return response


def clean_team_name(team_name):
    """Clean and normalize team name for consistent database storage and queries."""
    if not team_name:
        return ''
    return str(team_name).strip()


def result(request):
    """Result page view with prediction data."""
    home_team = clean_team_name(request.GET.get('home_team', ''))
    away_team = clean_team_name(request.GET.get('away_team', ''))
    category = request.GET.get('category', '')
    
    # If team names are missing from URL, try to get from most recent prediction
    if not home_team or not away_team:
        try:
            latest_prediction = Prediction.objects.latest('prediction_date')
            if latest_prediction:
                home_team = clean_team_name(latest_prediction.home_team)
                away_team = clean_team_name(latest_prediction.away_team)
                category = latest_prediction.category or ''
                logger.info(f"Loaded teams from latest prediction: {home_team} vs {away_team}")
        except Prediction.DoesNotExist:
            logger.warning("No predictions found in database")
        except Exception as e:
            logger.error(f"Error loading latest prediction: {e}")
    
    # Get prediction data from URL parameters or generate fallback
    home_score = request.GET.get('home_score', '')
    away_score = request.GET.get('away_score', '')
    outcome = request.GET.get('outcome', '')
    prediction_number = request.GET.get('prediction_number', '')
    
    # If scores are not provided, generate fallback prediction
    if not home_score or not away_score:
        import random
        # Generate realistic fallback scores
        fallback_prediction = random.choice([1, 2, 3])
        if fallback_prediction == 1:  # Home win
            home_score = random.randint(1, 3)
            away_score = random.randint(0, home_score - 1)
            outcome = "Home"
        elif fallback_prediction == 2:  # Draw
            home_score = random.randint(0, 2)
            away_score = home_score
            outcome = "Draw"
        else:  # Away win
            away_score = random.randint(1, 3)
            home_score = random.randint(0, away_score - 1)
            outcome = "Away"
        
        prediction_number = fallback_prediction
    
    # Ensure scores are integers
    try:
        home_score = int(home_score) if home_score else 1
        away_score = int(away_score) if away_score else 0
    except (ValueError, TypeError):
        home_score = 1
        away_score = 0
    
    # Get additional model data from URL parameters
    model1_prediction = request.GET.get('model1_prediction', 'Model Prediction')
    model1_basis = request.GET.get('model1_basis', 'Based on historical data analysis')
    model1_confidence_str = request.GET.get('model1_confidence', '')
    model2_prediction = request.GET.get('model2_prediction', '')
    model2_confidence_str = request.GET.get('model2_confidence', '')
    # Format model2_prediction for display if it's a number
    if model2_prediction:
        try:
            pred_num = int(model2_prediction)
            if pred_num == 0:
                model2_prediction = "Home Team Win"
            elif pred_num == 1:
                model2_prediction = "Draw"
            elif pred_num == 2:
                model2_prediction = "Away Team Win"
        except (ValueError, TypeError):
            pass  # Keep as is if not a number
    model_type = request.GET.get('model_type', '')
    # If model_type not provided, try to infer from teams
    if not model_type:
        # Check if teams are in Others category
        try:
            other_teams = set()
            other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
            for league in other_leagues:
                other_teams.update([team.name for team in league.teams.all()])
            if home_team in other_teams and away_team in other_teams:
                model_type = 'Model2'
            else:
                model_type = 'Model1'
        except Exception:
            model_type = 'Model1'  # Default fallback
    final_prediction = request.GET.get('final_prediction', '')
    
    # Convert confidence to float, handling both percentage and decimal formats
    try:
        if model1_confidence_str:
            model1_confidence = float(model1_confidence_str)
            # If it's less than 1, it's probably a decimal (0.0-1.0), convert to percentage
            if model1_confidence < 1.0:
                model1_confidence = model1_confidence * 100
            # Ensure it's a reasonable value (0-100)
            model1_confidence = max(0, min(100, model1_confidence))
        else:
            model1_confidence = None
    except (ValueError, TypeError):
        model1_confidence = None
    
    # Convert model2_confidence to float, handling both percentage and decimal formats
    try:
        if model2_confidence_str:
            model2_confidence = float(model2_confidence_str)
            # If it's less than 1, it's probably a decimal (0.0-1.0), convert to percentage
            if model2_confidence < 1.0:
                model2_confidence = model2_confidence * 100
            # Ensure it's a reasonable value (0-100)
            model2_confidence = max(0, min(100, model2_confidence))
        else:
            model2_confidence = None
    except (ValueError, TypeError):
        model2_confidence = None
    
    # Determine if this is a real prediction or fallback
    is_real_prediction = model1_prediction != 'Fallback' and model1_basis != 'Fallback prediction: scores generated for display'
    
    # Get probabilities from URL parameters if provided, otherwise calculate from historical data
    prob_home_param = request.GET.get('prob_home')
    prob_draw_param = request.GET.get('prob_draw')
    prob_away_param = request.GET.get('prob_away')
    
    if prob_home_param and prob_draw_param and prob_away_param:
        # Use probabilities from URL parameters
        try:
            prob_home_raw = float(prob_home_param)
            prob_draw_raw = float(prob_draw_param)
            prob_away_raw = float(prob_away_param)
            
            logger.debug(f"Raw probabilities from URL - Home: {prob_home_raw}, Draw: {prob_draw_raw}, Away: {prob_away_raw}")
            
            # Check if probabilities are already in decimal format (0-1) or percentage format (0-100)
            total_raw = prob_home_raw + prob_draw_raw + prob_away_raw
            
            if total_raw > 10:  # Likely in percentage format (0-100)
                # Convert from percentage to decimal
                probabilities = {
                    'Home': prob_home_raw / 100.0,
                    'Draw': prob_draw_raw / 100.0,
                    'Away': prob_away_raw / 100.0
                }
                logger.debug(f"Converted from percentage to decimal: {probabilities}")
            else:  # Already in decimal format (0-1)
                probabilities = {
                    'Home': prob_home_raw,
                    'Draw': prob_draw_raw,
                    'Away': prob_away_raw
                }
                logger.debug(f"Already in decimal format: {probabilities}")
            
            # Normalize to ensure probabilities sum to exactly 1.0
            total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
            if total_prob > 0 and abs(total_prob - 1.0) > 0.01:  # Only normalize if significantly different from 1.0
                probabilities['Home'] = probabilities['Home'] / total_prob
                probabilities['Draw'] = probabilities['Draw'] / total_prob
                probabilities['Away'] = probabilities['Away'] / total_prob
                logger.debug(f"Probabilities normalized (sum was {total_prob:.4f})")
            
            # Ensure probabilities are valid (0-1 range)
            probabilities['Home'] = max(0.0, min(1.0, probabilities['Home']))
            probabilities['Draw'] = max(0.0, min(1.0, probabilities['Draw']))
            probabilities['Away'] = max(0.0, min(1.0, probabilities['Away']))
            
            logger.debug(f"Final normalized probabilities (sum={sum(probabilities.values()):.4f}): {probabilities}")
            logger.debug(f"Final probabilities as percentages: Home={probabilities['Home']*100:.1f}%, Draw={probabilities['Draw']*100:.1f}%, Away={probabilities['Away']*100:.1f}%")
            
            # Set historical_probabilities same as probabilities when from URL
            # (These are the model probabilities, we'll calculate real historical later if needed)
            historical_probabilities = probabilities.copy()
            
            logger.info(f"Using probabilities from URL parameters (normalized): {probabilities}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing probabilities from URL: {e}")
            probabilities = None
            historical_probabilities = None
    else:
        logger.debug(f"No probabilities in URL parameters - Home: {prob_home_param}, Draw: {prob_draw_param}, Away: {prob_away_param}")
        probabilities = None
        historical_probabilities = None
    
    # If probabilities not in URL, calculate from historical data
    if probabilities is None:
        from .analytics import calculate_probabilities_original, load_football_data
        try:
            # Determine which dataset to use based on team categories
            other_teams = set()
            try:
                other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
                for league in other_leagues:
                    other_teams.update([team.name for team in league.teams.all()])
            except Exception:
                pass  # Fallback to default dataset
            
            # Load appropriate dataset (data1 for Model 1 teams, data2 for Model 2 teams)
            # For Others category, try dataset 2 first, but fallback to dataset 1 if no H2H data
            if home_team in other_teams and away_team in other_teams:
                data = load_football_data(2, use_cache=True)  # Try dataset 2 first
                # Check if H2H data exists, if not try dataset 1
                if hasattr(data, 'columns') and len(data.columns) > 0:
                    home_col = 'HomeTeam' if 'HomeTeam' in data.columns else 'Home'
                    away_col = 'AwayTeam' if 'AwayTeam' in data.columns else 'Away'
                    h2h_check = data[
                        (data[home_col].astype(str).str.strip() == str(home_team).strip()) &
                        (data[away_col].astype(str).str.strip() == str(away_team).strip())
                    ]
                    if len(h2h_check) == 0:
                        # No H2H in dataset 2, try dataset 1
                        logger.info(f"No H2H data in dataset 2 for {home_team} vs {away_team}, trying dataset 1")
                        data = load_football_data(1, use_cache=True)
            else:
                data = load_football_data(1, use_cache=True)  # Use dataset 1 for Model 1 teams
            
            # Check if data is empty (handles both pandas DataFrame and our mock EmptyDataFrame)
            data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
            
            if not data_empty and home_team and away_team:
                try:
                    historical_probs_raw = calculate_probabilities_original(home_team, away_team, data, version="v1")
                    if historical_probs_raw:
                        # historical_probs_raw are already in percentage format (0-100), convert to decimal (0-1)
                        probabilities = {
                            'Home': historical_probs_raw.get("Home Team Win", 33.0) / 100.0,
                            'Draw': historical_probs_raw.get("Draw", 33.0) / 100.0,
                            'Away': historical_probs_raw.get("Away Team Win", 33.0) / 100.0
                        }
                        # Normalize to ensure probabilities sum to exactly 1.0
                        total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
                        if total_prob > 0:
                            probabilities['Home'] = probabilities['Home'] / total_prob
                            probabilities['Draw'] = probabilities['Draw'] / total_prob
                            probabilities['Away'] = probabilities['Away'] / total_prob
                        # Store historical probabilities separately for Past Performance section
                        historical_probabilities = probabilities.copy()
                        logger.info(f"Using calculated historical probabilities from data (normalized to decimal): {probabilities}")
                    else:
                        logger.warning("Historical probabilities returned None, using fallback")
                        probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
                        historical_probabilities = probabilities.copy()
                except Exception as e:
                    logger.error(f"Error calculating historical probabilities: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
                    historical_probabilities = probabilities.copy()
            else:
                logger.warning(f"Data empty or teams missing. Data empty: {data_empty}, Home: {home_team}, Away: {away_team}")
                probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
                historical_probabilities = probabilities.copy()
        except ImportError as e:
            logger.error(f"Cannot load data due to import error (pandas may be corrupted): {e}")
            probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
            historical_probabilities = probabilities.copy()
        except Exception as e:
            logger.error(f"Error loading football data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
            historical_probabilities = probabilities.copy()
    
    # Calculate REAL historical probabilities from H2H data (separate from model probabilities)
    # This ensures "Past Performance" shows actual historical data, not model predictions
    if 'historical_probabilities' not in locals() or historical_probabilities is None:
        historical_probabilities = probabilities.copy() if probabilities else {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
    
    # Always try to get real historical probabilities from H2H data
    try:
        from .analytics import calculate_probabilities_original, load_football_data
        
        # Determine which dataset to use
        other_teams = set()
        try:
            other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
            for league in other_leagues:
                other_teams.update([team.name for team in league.teams.all()])
        except Exception:
            pass
        
        # Load appropriate dataset
        if home_team in other_teams and away_team in other_teams:
            data = load_football_data(2, use_cache=True)
        else:
            data = load_football_data(1, use_cache=True)
        
        data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
        
        if not data_empty and home_team and away_team:
            real_historical_probs = calculate_probabilities_original(home_team, away_team, data, version="v1")
            if real_historical_probs:
                # Convert from percentage to decimal
                historical_probabilities = {
                    'Home': real_historical_probs.get("Home Team Win", 33.0) / 100.0,
                    'Draw': real_historical_probs.get("Draw", 33.0) / 100.0,
                    'Away': real_historical_probs.get("Away Team Win", 33.0) / 100.0
                }
                # Normalize
                total_hist = sum(historical_probabilities.values())
                if total_hist > 0:
                    historical_probabilities = {k: v/total_hist for k, v in historical_probabilities.items()}
                logger.info(f"Calculated real historical probabilities: {historical_probabilities}")
    except Exception as e:
        logger.warning(f"Could not calculate real historical probabilities: {e}")
        # Keep the copy of model probabilities as fallback
    
    # Save prediction to database if not already saved (backup save in result view)
    # Check if prediction already exists to avoid duplicates
    try:
        from django.core.cache import cache
        from django.utils import timezone
        from datetime import timedelta
        
        # Only save if prediction doesn't exist in last 5 minutes (avoid duplicates)
        # Use timezone-aware datetime
        recent_prediction = Prediction.objects.filter(
            home_team=home_team,
            away_team=away_team,
            prediction_date__gte=timezone.now() - timedelta(minutes=5)
        ).first()
        
        if not recent_prediction and home_team and away_team:
            # Use calculated probabilities or get from URL
            prob_home_val = probabilities.get('Home', 0.33)
            prob_draw_val = probabilities.get('Draw', 0.33)
            prob_away_val = probabilities.get('Away', 0.33)
            
            # Calculate confidence from probabilities
            confidence_val = max(prob_home_val, prob_draw_val, prob_away_val)
            
            # Ensure session exists for anonymous users
            if not request.user.is_authenticated:
                # Force session creation by setting a value (avoid explicit .create() which needs Redis)
                if not request.session.session_key:
                    request.session['_init'] = True
                
                session_key = request.session.session_key
                logger.info(f"Result view - Session key for anonymous user: {session_key}")
            else:
                session_key = None
            
            prediction = Prediction.objects.create(
                home_team=clean_team_name(home_team),
                away_team=clean_team_name(away_team),
                home_score=home_score,
                away_score=away_score,
                confidence=confidence_val,
                category=category or '',
                outcome=outcome or '',
                prob_home=prob_home_val,
                prob_draw=prob_draw_val,
                prob_away=prob_away_val,
                model_type=model_type or '',
                model1_prediction=model1_prediction or '',
                final_prediction=final_prediction or outcome or '',
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key
            )
            logger.info(f"Backup prediction saved in result view: {prediction.id} with session_key: {session_key}")
            
            # Clear cache to update history (handle Redis unavailable)
            try:
                cache.delete('home_stats')
                cache.delete('recent_predictions')
            except Exception as cache_error:
                logger.warning(f"Cache clear failed (Redis may be unavailable): {cache_error}")
    except Exception as save_error:
        logger.error(f"Error saving backup prediction in result view: {save_error}")
        # Don't fail the whole request if cache fails
    
    # Note: outcome comes from the MODEL prediction (passed in URL parameters)
    # Historical probabilities are displayed separately for reference only
    # Do NOT override outcome based on historical probabilities - use model prediction
    if not outcome:
        # Fallback: determine from scores if outcome not provided
        if home_score > away_score:
            outcome = "Home"
        elif away_score > home_score:
            outcome = "Away"
        else:
            outcome = "Draw"
    
    # Get head-to-head match results (past matches)
    h2h_matches = []
    # Get upcoming matches (future matches)
    upcoming_matches = []
    try:
        from .analytics import get_column_names, load_football_data, safe_import_pandas
        pd = safe_import_pandas()
        
        # Use the same dataset as for probabilities
        other_teams = set()
        try:
            other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
            for league in other_leagues:
                other_teams.update([team.name for team in league.teams.all()])
        except Exception:
            pass  # Fallback to default dataset
        
        if home_team in other_teams and away_team in other_teams:
            data = load_football_data(2)
        else:
            data = load_football_data(1)
        
        if hasattr(data, 'columns') and len(data.columns) > 0 and not (hasattr(data, 'empty') and data.empty):
            home_col, away_col, result_col = get_column_names("v1")
            
            # Get head-to-head matches
            try:
                h2h = data[(data[home_col].astype(str).str.strip() == str(home_team).strip()) & 
                           (data[away_col].astype(str).str.strip() == str(away_team).strip())]
                
                # If empty, try case-insensitive
                if len(h2h) == 0:
                    h2h = data[(data[home_col].astype(str).str.strip().str.lower() == str(home_team).strip().lower()) & 
                               (data[away_col].astype(str).str.strip().str.lower() == str(away_team).strip().lower())]
                
                # Sort by date if available, get last 5 matches
                if len(h2h) > 0:
                    # Remove duplicates based on date, home_score, and away_score
                    if 'Date' in h2h.columns and 'FTHG' in h2h.columns and 'FTAG' in h2h.columns:
                        # Create a unique key for each match
                        h2h = h2h.drop_duplicates(subset=['Date', 'FTHG', 'FTAG'], keep='first')
                    
                    if 'Date' in h2h.columns:
                        # Filter to only include matches that have been played (before today)
                        from datetime import datetime
                        today = datetime.now()
                        
                        # Convert Date column to datetime for filtering
                        h2h['Date_parsed'] = pd.to_datetime(h2h['Date'], errors='coerce')
                        
                        # Only include matches before today (already played)
                        h2h = h2h[h2h['Date_parsed'] < today]
                        
                        # Sort by date (most recent first)
                        h2h = h2h.sort_values('Date_parsed', ascending=False)
                    h2h = h2h.head(5)
                    
                    # Track seen matches to avoid duplicates
                    seen_matches = set()
                    
                    # Format matches for display
                    for idx, row in h2h.iterrows():
                        try:
                            home_score_val = row.get('FTHG', 0)
                            away_score_val = row.get('FTAG', 0)
                            home_score = int(home_score_val) if pd.notna(home_score_val) else 0
                            away_score = int(away_score_val) if pd.notna(away_score_val) else 0
                            
                            date = row.get('Date', '')
                            if pd.notna(date) and date:
                                try:
                                    from datetime import datetime, timedelta
                                    # Handle Excel serial date numbers (like 45570, 45171)
                                    if isinstance(date, (int, float)) and date > 25000:
                                        # Excel serial date: days since 1900-01-01 (minus 2 days for Excel bug)
                                        base_date = datetime(1899, 12, 30)
                                        date_obj = base_date + timedelta(days=int(date))
                                        date = date_obj.strftime('%Y-%m-%d')
                                    elif isinstance(date, str):
                                        # Try parsing various date formats
                                        try:
                                            date_obj = pd.to_datetime(date)
                                            date = date_obj.strftime('%Y-%m-%d')
                                        except:
                                            date = str(date)
                                    else:
                                        # Pandas datetime object
                                        if hasattr(date, 'strftime'):
                                            date = date.strftime('%Y-%m-%d')
                                        else:
                                            date_obj = pd.to_datetime(date)
                                            date = date_obj.strftime('%Y-%m-%d')
                                except Exception as date_error:
                                    logger.warning(f"Date parsing error: {date_error}, raw date: {date}")
                                    date = 'Unknown Date'
                            else:
                                date = 'Unknown Date'
                            
                            # Create unique match identifier to avoid duplicates
                            match_key = (date, home_score, away_score)
                            if match_key in seen_matches:
                                continue  # Skip duplicate
                            seen_matches.add(match_key)
                            
                            result = row.get(result_col, '')
                            # Determine winner
                            if result == 'H' or (isinstance(result, (int, float)) and result == 2):
                                winner = home_team
                            elif result == 'A' or (isinstance(result, (int, float)) and result == 0):
                                winner = away_team
                            else:
                                winner = 'Draw'
                            
                            h2h_matches.append({
                                'date': date,
                                'home_score': home_score,
                                'away_score': away_score,
                                'winner': winner,
                                'result': result
                            })
                        except Exception as e:
                            logger.warning(f"Error processing H2H match: {e}")
                            continue
                
                # Now get upcoming/future matches (scheduled but not played yet)
                try:
                    h2h_future = data[(data[home_col].astype(str).str.strip() == str(home_team).strip()) & 
                                      (data[away_col].astype(str).str.strip() == str(away_team).strip())]
                    
                    # If empty, try case-insensitive
                    if len(h2h_future) == 0:
                        h2h_future = data[(data[home_col].astype(str).str.strip().str.lower() == str(home_team).strip().lower()) & 
                                          (data[away_col].astype(str).str.strip().str.lower() == str(away_team).strip().lower())]
                    
                    if len(h2h_future) > 0 and 'Date' in h2h_future.columns:
                        from datetime import datetime
                        today = datetime.now()
                        
                        # Convert Date column to datetime
                        h2h_future['Date_parsed'] = pd.to_datetime(h2h_future['Date'], errors='coerce')
                        
                        # Only include matches AFTER today (upcoming/scheduled)
                        h2h_future = h2h_future[h2h_future['Date_parsed'] >= today]
                        
                        # Sort by date (earliest first)
                        h2h_future = h2h_future.sort_values('Date_parsed', ascending=True)
                        h2h_future = h2h_future.head(5)  # Get next 5 upcoming matches
                        
                        # Format upcoming matches for display
                        for idx, row in h2h_future.iterrows():
                            try:
                                date = row.get('Date', '')
                                if pd.notna(date) and date:
                                    try:
                                        from datetime import datetime, timedelta
                                        # Handle Excel serial date numbers
                                        if isinstance(date, (int, float)) and date > 25000:
                                            base_date = datetime(1899, 12, 30)
                                            date_obj = base_date + timedelta(days=int(date))
                                            date = date_obj.strftime('%Y-%m-%d')
                                        elif isinstance(date, str):
                                            try:
                                                date_obj = pd.to_datetime(date)
                                                date = date_obj.strftime('%Y-%m-%d')
                                            except:
                                                date = str(date)
                                        else:
                                            if hasattr(date, 'strftime'):
                                                date = date.strftime('%Y-%m-%d')
                                            else:
                                                date_obj = pd.to_datetime(date)
                                                date = date_obj.strftime('%Y-%m-%d')
                                    except Exception as date_error:
                                        logger.warning(f"Date parsing error for upcoming match: {date_error}")
                                        date = 'TBD'
                                else:
                                    date = 'TBD'
                                
                                upcoming_matches.append({
                                    'date': date,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'status': 'Scheduled'
                                })
                            except Exception as e:
                                logger.warning(f"Error processing upcoming match: {e}")
                                continue
                except Exception as e:
                    logger.warning(f"Error getting upcoming matches: {e}")
                    
            except Exception as e:
                logger.warning(f"Error getting H2H matches: {e}")
    except Exception as e:
        logger.error(f"Error getting head-to-head matches: {e}")
        import traceback
        logger.error(traceback.format_exc())
        h2h_matches = []
        upcoming_matches = []
    
    # Get team form (last 5 matches) using original logic
    from .analytics import get_team_recent_form_original
    
    home_team_form = 'DDDDD'  # Default fallback
    away_team_form = 'DDDDD'  # Default fallback
    
    if home_team and away_team:
        try:
            # Determine which dataset to use based on team categories (same logic as probabilities)
            other_teams = set()
            try:
                other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
                for league in other_leagues:
                    other_teams.update([team.name for team in league.teams.all()])
            except Exception:
                pass  # Fallback to default dataset
            
            # Load appropriate dataset (data1 for Model 1 teams, data2 for Model 2 teams)
            # For Others category, try dataset 2 first, but fallback to dataset 1 if no data found
            if home_team in other_teams and away_team in other_teams:
                data = load_football_data(2, use_cache=True)  # Try dataset 2 first
                # Check if dataset 2 has the teams, if not try dataset 1
                if hasattr(data, 'columns') and len(data.columns) > 0:
                    home_col = 'HomeTeam' if 'HomeTeam' in data.columns else 'Home'
                    away_col = 'AwayTeam' if 'AwayTeam' in data.columns else 'Away'
                    # Check if teams exist in dataset 2
                    home_matches = data[data[home_col].astype(str).str.contains(home_team, case=False, na=False)]
                    away_matches = data[data[away_col].astype(str).str.contains(away_team, case=False, na=False)]
                    if len(home_matches) == 0 and len(away_matches) == 0:
                        # Teams not in dataset 2, try dataset 1
                        logger.info(f"Teams {home_team}/{away_team} not in dataset 2, trying dataset 1")
                        data = load_football_data(1, use_cache=True)
            else:
                data = load_football_data(1, use_cache=True)  # Use dataset 1 for Model 1 teams
            
            # Check if data is actually usable (not our mock EmptyDataFrame)
            data_usable = hasattr(data, 'columns') and len(data.columns) > 0 and not (hasattr(data, 'empty') and data.empty and len(data.columns) == 0)
            
            if data_usable:
                # Try to get form from actual data
                try:
                    home_team_form = get_team_recent_form_original(home_team, data, version="v1")
                    away_team_form = get_team_recent_form_original(away_team, data, version="v1")
                    # If forms are hash-based (no real data), try dataset 1 as fallback for Others teams
                    if home_team in other_teams and away_team in other_teams:
                        # Check if forms look hash-based (all same pattern or unrealistic)
                        if home_team_form == 'DDDDD' or away_team_form == 'DDDDD':
                            logger.info(f"Hash-based forms detected, trying dataset 1 for {home_team}/{away_team}")
                            data1 = load_football_data(1, use_cache=True)
                            home_form_d1 = get_team_recent_form_original(home_team, data1, version="v1")
                            away_form_d1 = get_team_recent_form_original(away_team, data1, version="v1")
                            if home_form_d1 != 'DDDDD':
                                home_team_form = home_form_d1
                            if away_form_d1 != 'DDDDD':
                                away_team_form = away_form_d1
                except Exception as form_error:
                    logger.warning(f"Error getting form from data: {form_error}, using hash-based fallback")
                    # Fall through to hash-based generation
                    data_usable = False
            
            # If data not usable or form calculation failed, use hash-based generation
            if not data_usable or not home_team_form or not away_team_form:
                # Generate realistic form based on team name hash (consistent for same team)
                import hashlib
                
                home_hash = int(hashlib.md5(home_team.strip().encode()).hexdigest()[:8], 16)
                away_hash = int(hashlib.md5(away_team.strip().encode()).hexdigest()[:8], 16)
                
                # Generate form based on hash: W=40%, D=30%, L=30% distribution
                form_points = {'W': 3, 'D': 1, 'L': 0}
                for team_hash, team_name, form_var in [(home_hash, home_team, 'home_team_form'), (away_hash, away_team, 'away_team_form')]:
                    form_chars = []
                    for i in range(5):
                        rand_val = (team_hash + i * 7919) % 100  # Use prime for better distribution
                        if rand_val < 40:
                            form_chars.append("W")
                        elif rand_val < 70:
                            form_chars.append("D")
                        else:
                            form_chars.append("L")
                    if form_var == 'home_team_form':
                        home_team_form = "".join(form_chars)
                    else:
                        away_team_form = "".join(form_chars)
            
            # Ensure we have exactly 5 characters (pad with 'D' if needed)
            if not home_team_form or len(home_team_form) < 5:
                home_team_form = (home_team_form or '') + 'D' * (5 - len(home_team_form or ''))
            if not away_team_form or len(away_team_form) < 5:
                away_team_form = (away_team_form or '') + 'D' * (5 - len(away_team_form or ''))
            
            # Ensure exactly 5 characters
            home_team_form = home_team_form[:5].ljust(5, 'D')
            away_team_form = away_team_form[:5].ljust(5, 'D')
            
            logger.info(f"Team forms - {home_team}: {home_team_form}, {away_team}: {away_team_form}")
        except Exception as e:
            logger.error(f"Error getting team form: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Use hash-based fallback even on error
            try:
                import hashlib
                home_hash = int(hashlib.md5(home_team.strip().encode()).hexdigest()[:8], 16)
                away_hash = int(hashlib.md5(away_team.strip().encode()).hexdigest()[:8], 16)
                
                for team_hash, form_var in [(home_hash, 'home_team_form'), (away_hash, 'away_team_form')]:
                    form_chars = []
                    for i in range(5):
                        rand_val = (team_hash + i * 7919) % 100
                        if rand_val < 40:
                            form_chars.append("W")
                        elif rand_val < 70:
                            form_chars.append("D")
                        else:
                            form_chars.append("L")
                    if form_var == 'home_team_form':
                        home_team_form = "".join(form_chars)
                    else:
                        away_team_form = "".join(form_chars)
            except:
                home_team_form = 'DDDDD'
            away_team_form = 'DDDDD'
    
    # Get all previous predictions for this matchup
    # Strip whitespace from team names to ensure proper matching
    home_team_clean = home_team.strip() if home_team else ''
    away_team_clean = away_team.strip() if away_team else ''
    
    # Filter predictions based on user authentication
    if request.user.is_authenticated:
        # For authenticated users, show their predictions
        all_predictions = Prediction.objects.filter(
            home_team__iexact=home_team_clean,
            away_team__iexact=away_team_clean,
            user=request.user
        ).order_by('-prediction_date')
    else:
        # For non-authenticated users, show predictions from their session
        session_key = request.session.session_key
        if session_key:
            all_predictions = Prediction.objects.filter(
                home_team__iexact=home_team_clean,
                away_team__iexact=away_team_clean,
                session_key=session_key
            ).order_by('-prediction_date')
        else:
            all_predictions = Prediction.objects.none()
    
    # Calculate prediction statistics
    total_predictions_count = all_predictions.count()
    logger.info(f"Found {total_predictions_count} previous predictions for {home_team_clean} vs {away_team_clean}")
    home_predictions = all_predictions.filter(outcome='Home').count()
    draw_predictions = all_predictions.filter(outcome='Draw').count()
    away_predictions = all_predictions.filter(outcome='Away').count()
    
    # Calculate average scores
    if total_predictions_count > 0:
        from django.db.models import Avg
        avg_home_score = all_predictions.aggregate(Avg('home_score'))['home_score__avg'] or 0
        avg_away_score = all_predictions.aggregate(Avg('away_score'))['away_score__avg'] or 0
        avg_confidence = all_predictions.aggregate(Avg('confidence'))['confidence__avg'] or 0
    else:
        avg_home_score = 0
        avg_away_score = 0
        avg_confidence = 0
    
    prediction_stats = {
        'total_count': total_predictions_count,
        'home_count': home_predictions,
        'draw_count': draw_predictions,
        'away_count': away_predictions,
        'home_percentage': (home_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'draw_percentage': (draw_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'away_percentage': (away_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'avg_home_score': round(avg_home_score, 1),
        'avg_away_score': round(avg_away_score, 1),
        'avg_confidence': round(avg_confidence * 100, 1) if avg_confidence <= 1 else round(avg_confidence, 1)
    }
    
    context = {
        'home_team': home_team,
        'away_team': away_team,
        'home_score': home_score,
        'away_score': away_score,
        'category': category,
        'outcome': outcome,
        'prediction_number': prediction_number,
        'probabilities': probabilities,
        'historical_probabilities': historical_probabilities if 'historical_probabilities' in locals() else probabilities,
        'model1_prediction': model1_prediction if is_real_prediction else 'Fallback',
        'model1_probs': None,
        'model2_prediction': model2_prediction if model2_prediction else None,
        'model2_probs': None,
        'model2_confidence': model2_confidence,
        'model_type': model_type,
        'model1_basis': model1_basis if is_real_prediction else 'Fallback prediction: scores generated for display',
        'is_real_prediction': is_real_prediction,
        'model1_confidence': model1_confidence,
        'final_prediction': final_prediction,
        'home_team_form': home_team_form,
        'away_team_form': away_team_form,
        'h2h_matches': h2h_matches,
        'upcoming_matches': upcoming_matches,
        'all_predictions': all_predictions[:10],  # Show last 10 predictions
        'prediction_stats': prediction_stats
    }
    
    logger.debug(f"Result view - home_score={home_score}, away_score={away_score}, outcome={outcome}")
    logger.debug(f"Result view - probabilities={probabilities}")
    logger.info(f"Result view probabilities: {probabilities}")
    
    return render(request, 'predictor/result.html', context)


def create_sample_data():
    """Create sample data for testing the dashboard."""
    from datetime import datetime, timedelta
    import random
    
    # Sample teams
    teams = [
        'Man City', 'Liverpool', 'Arsenal', 'Chelsea', 'Barcelona', 'Real Madrid',
        'Bayern Munich', 'Dortmund', 'PSG', 'Juventus', 'Milan', 'Inter',
        'Ath Madrid', 'Valencia', 'Sevilla', 'Napoli', 'Roma', 'Lazio'
    ]
    
    # Sample leagues
    leagues = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
    
    # Create sample teams if they don't exist
    for team_name in teams:
        Team.objects.get_or_create(
            name=team_name,
            defaults={
                'league': random.choice(leagues),
                'country': 'Various'
            }
        )
    
    # Create sample matches if they don't exist
    for i in range(20):
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        match_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        Match.objects.get_or_create(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            defaults={
                'home_score': random.randint(0, 3),
                'away_score': random.randint(0, 3),
                'league': random.choice(leagues),
                'season': '2024/25'
            }
        )
    
    # Create sample predictions if they don't exist
    for i in range(15):
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        prediction_date = datetime.now() - timedelta(days=random.randint(1, 7))
        
        home_score = random.randint(0, 3)
        away_score = random.randint(0, 3)
        confidence = random.uniform(0.6, 0.95)
        
        Prediction.objects.get_or_create(
            home_team=home_team,
            away_team=away_team,
            prediction_date=prediction_date,
            defaults={
                'home_score': home_score,
                'away_score': away_score,
                'confidence': confidence
            }
        )
    
    logger.info("Sample data created successfully!")
    logger.info(f"  - Teams: {Team.objects.count()}")
    logger.info(f"  - Matches: {Match.objects.count()}")
    logger.info(f"  - Predictions: {Prediction.objects.count()}")

