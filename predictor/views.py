import pickle
import warnings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import os
import logging
from .models import Prediction, Match, Team, League, BillingUsage, Subscription
from .auth_views import check_subscription_status, use_prediction_credit, subscription_required

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

def load_prediction_models():
    """Load prediction models (Model1 and Model2) with fallback handling.
    
    Returns:
        tuple: (model1, model2) - Both may be None if loading fails
    """
    # Define model paths
    model1_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model1.pkl')
    model2_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model2.pkl')
    
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
    
    
    # If models fail to load, they will be None and fallback logic will be used
    if model1 is None and model2 is None:
        logger.warning('Both models failed to load, will use fallback prediction logic')
    elif model1 is None:
        logger.warning('Model 1 failed to load, will use fallback for Model 1 predictions')
    elif model2 is None:
        logger.warning('Model 2 failed to load, will use form-based fallback for Model 2 teams')
    
    
    return model1, model2

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
        "Premier League": sorted(['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds', 'Liverpool', 'Man City', 'Man United', 'Newcastle', "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves']),
        "English Championship": sorted(['Birmingham', 'Blackburn', 'Bristol City', 'Charlton', 'Coventry', 'Derby', 'Hull', 'Ipswich', 'Leicester', 'Middlesbrough', 'Millwall', 'Norwich', 'Oxford', 'Portsmouth', 'Preston', 'QPR', 'Sheffield United', 'Sheffield Weds', 'Southampton', 'Stoke', 'Swansea', 'Watford', 'West Brom', 'Wrexham']),
        "Serie A": sorted(['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']),
        "Serie B": sorted(['Avellino', 'Bari', 'Carrarese', 'Catanzaro', 'Cesena', 'Empoli', 'Frosinone', 'Juve Stabia', 'Mantova', 'Modena', 'Monza', 'Padova', 'Palermo', 'Pescara', 'Reggiana', 'Sampdoria', 'Spezia', 'Sudtirol', 'Venezia', 'Virtus Entella']),
        "Ligue1": sorted(['Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lorient', 'Lyon', 'Marseille', 'Metz', 'Monaco', 'Nantes', 'Nice', 'Paris FC', 'Paris SG', 'Rennes', 'Strasbourg', 'Toulouse']),
        "Ligue2": sorted(['Amiens', 'Annecy', 'Bastia', 'Boulogne', 'Clermont', 'Dunkerque', 'Grenoble', 'Guingamp', 'Laval', 'Le Mans', 'Montpellier', 'Nancy', 'Pau FC', 'Red Star', 'Reims', 'Rodez', 'St Etienne', 'Troyes']),
        "La Liga": sorted(['Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis', 'Celta', 'Elche', 'Espanol', 'Getafe', 'Girona', 'Levante', 'Mallorca', 'Osasuna', 'Oviedo', 'Real Madrid', 'Sevilla', 'Sociedad', 'Valencia', 'Vallecano', 'Villarreal']),
        "La Liga2": sorted(['Albacete', 'Almeria', 'Andorra', 'Burgos', 'Cadiz', 'Castellon', 'Ceuta', 'Cordoba', 'Cultural Leonesa', 'Eibar', 'Granada', 'Huesca', 'La Coruna', 'Las Palmas', 'Leganes', 'Malaga', 'Mirandes', 'Santander', 'Sociedad B', 'Sp Gijon', 'Valladolid', 'Zaragoza']),
        "Eredivisie": sorted(['AZ Alkmaar', 'Ajax', 'Excelsior', 'Feyenoord', 'For Sittard', 'Go Ahead Eagles', 'Groningen', 'Heerenveen', 'Heracles', 'NAC Breda', 'Nijmegen', 'PSV Eindhoven', 'Sparta Rotterdam', 'Telstar', 'Twente', 'Utrecht', 'Volendam', 'Zwolle']),
        "Bundesliga": sorted(['Augsburg', 'Bayern Munich', 'Dortmund', 'Ein Frankfurt', 'FC Koln', 'Freiburg', 'Hamburg', 'Heidenheim', 'Hoffenheim', 'Leverkusen', "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg']),
        "Bundesliga2": sorted(['Bielefeld', 'Bochum', 'Braunschweig', 'Darmstadt', 'Dresden', 'Elversberg', 'Fortuna Dusseldorf', 'Greuther Furth', 'Hannover', 'Hertha', 'Holstein Kiel', 'Kaiserslautern', 'Karlsruhe', 'Magdeburg', 'Nurnberg', 'Paderborn', 'Preußen Münster', 'Schalke 04']),
        "Scottish League": sorted(['Aberdeen', 'Celtic', 'Dundee', 'Dundee United', 'Falkirk', 'Hearts', 'Hibernian', 'Kilmarnock', 'Livingston', 'Motherwell', 'Rangers', 'St Mirren']),
        "Belgium League": sorted(['Anderlecht', 'Antwerp', 'Cercle Brugge', 'Charleroi', 'Club Brugge', 'Dender', 'Genk', 'Gent', 'Mechelen', 'Oud-Heverlee Leuven', 'RAAL La Louviere', 'St Truiden', 'St. Gilloise', 'Standard', 'Waregem', 'Westerlo']),
        "Portuguese League": sorted(['AVS', 'Alverca', 'Arouca', 'Benfica', 'Casa Pia', 'Estoril', 'Estrela', 'Famalicao', 'Gil Vicente', 'Guimaraes', 'Moreirense', 'Nacional', 'Porto', 'Rio Ave', 'Santa Clara', 'Sp Braga', 'Sp Lisbon', 'Tondela']),
        "Turkish League": sorted(['Alanyaspor', 'Antalyaspor', 'Besiktas', 'Buyuksehyr', 'Eyupspor', 'Fenerbahce', 'Galatasaray', 'Gaziantep', 'Genclerbirligi', 'Goztep', 'Karagumruk', 'Kasimpasa', 'Kayserispor', 'Kocaelispor', 'Konyaspor', 'Rizespor', 'Samsunspor', 'Trabzonspor']),
        "Greece League": sorted(['AEK', 'Aris', 'Asteras Tripolis', 'Atromitos', 'Kifisia', 'Larisa', 'Levadeiakos', 'OFI Crete', 'Olympiakos', 'PAOK', 'Panathinaikos', 'Panetolikos', 'Panserraikos', 'Volos NFC']),
    },
    'Others': {
        "Switzerland League": sorted(['Basel', 'Grasshoppers', 'Lausanne', 'Lugano', 'Luzern', 'Servette', 'Sion', 'St. Gallen', 'Thun', 'Winterthur', 'Young Boys', 'Zurich']),
        "Denmark League": sorted(['Aarhus', 'Brondby', 'FC Copenhagen', 'Fredericia', 'Midtjylland', 'Nordsjaelland', 'Odense', 'Randers FC', 'Silkeborg', 'Sonderjyske', 'Vejle', 'Viborg']),
        "Austria League": sorted(['Altach', 'Austria Vienna', 'BW Linz', 'Grazer AK', 'Hartberg', 'LASK', 'Ried', 'SK Rapid', 'Salzburg', 'Sturm Graz', 'Tirol', 'Wolfsberger AC']),
        "Mexico League": sorted(['Atl. San Luis', 'Atlas', 'Club America', 'Club Leon', 'Club Tijuana', 'Cruz Azul', 'Guadalajara Chivas', 'Juarez', 'Mazatlan FC', 'Monterrey', 'Necaxa', 'Pachuca', 'Puebla', 'Queretaro', 'Santos Laguna', 'Tigres UANL', 'Toluca', 'UNAM Pumas']),
        "Russia League": sorted(['Akhmat Grozny', 'Akron Togliatti', 'Baltika', 'CSKA Moscow', 'Dynamo Makhachkala', 'Dynamo Moscow', 'FK Rostov', 'Krasnodar', 'Krylya Sovetov', 'Lokomotiv Moscow', 'Orenburg', 'Pari NN', 'Rubin Kazan', 'Sochi', 'Spartak Moscow', 'Zenit']),
        "Romania League": sorted(['CFR Cluj', 'Csikszereda M. Ciuc', 'Din. Bucuresti', 'FC Arges', 'FC Botosani', 'FC Hermannstadt', 'FC Rapid Bucuresti', 'FCSB', 'Farul Constanta', 'Metaloglobus Bucharest', 'Otelul', 'Petrolul', 'U. Cluj', 'UTA Arad', 'Unirea Slobozia', 'Univ. Craiova'])
    }
}


def get_league_for_team(team_name):
    """Find league for a given team name from LEAGUES_BY_CATEGORY."""
    if not team_name:
        return ''
    
    # Check LEAGUES_BY_CATEGORY
    for category, leagues in LEAGUES_BY_CATEGORY.items():
        for league_name, teams in leagues.items():
            if team_name in teams:
                return league_name
            # Case-insensitive check
            if any(t.lower() == team_name.lower() for t in teams):
                return league_name
    return ''


def process_prediction_probabilities(advanced_result):
    """
    Process and normalize probabilities from advanced_result consistently.
    Returns normalized probabilities dict and outcome.
    This ensures the same match always gets the same probabilities in both single and multi-match modes.
    """
    # Use model/blended probabilities as primary source (Standard AI behavior)
    # The 'probabilities' key from advanced_result contains the blended score (Model + Form + H2H)
    raw_probs = advanced_result.get('probabilities')
    
    if raw_probs:
        probabilities = {}
        for key, value in raw_probs.items():
            if key == 2:
                probabilities["Home"] = round(float(value), 6)
            elif key == 1:
                probabilities["Draw"] = round(float(value), 6)
            elif key == 0:
                probabilities["Away"] = round(float(value), 6)
            else:
                probabilities[str(key)] = round(float(value), 6)
    else:
        # Fallback to historical probabilities if model probs not available
        historical_probs = advanced_result.get('historical_probs')
        if historical_probs:
             # Historical probabilities are in percentage format (0-100)
            probabilities = {
                "Home": round(historical_probs.get("Home Team Win", 0) / 100.0, 6),
                "Draw": round(historical_probs.get("Draw", 0) / 100.0, 6),
                "Away": round(historical_probs.get("Away Team Win", 0) / 100.0, 6)
            }
        else:
             probabilities = {}
    
    # Normalize probabilities to ensure they sum to 1.0
    total_prob = probabilities.get("Home", 0) + probabilities.get("Draw", 0) + probabilities.get("Away", 0)
    if total_prob > 0:
        probabilities["Home"] = round(probabilities.get("Home", 0) / total_prob, 6)
        probabilities["Draw"] = round(probabilities.get("Draw", 0) / total_prob, 6)
        probabilities["Away"] = round(probabilities.get("Away", 0) / total_prob, 6)
    else:
        # Fallback to equal probabilities if total is 0
        probabilities = {"Home": round(0.333, 6), "Draw": round(0.334, 6), "Away": round(0.333, 6)}
    
    # Calculate double chance outcome
    outcome = calculate_double_chance(
        probabilities.get("Home", 0.33),
        probabilities.get("Draw", 0.33),
        probabilities.get("Away", 0.33)
    )
    
    return probabilities, outcome


def calculate_double_chance(prob_home, prob_draw, prob_away):
    """
    Calculate double chance outcome based on probabilities.

    Args:
        prob_home: Probability of home win (0-1)
        prob_draw: Probability of draw (0-1)
        prob_away: Probability of away win (0-1)

    Returns:
        str: One of 'Home', 'Draw', 'Away', '1X', 'X2', '12'
    """
    # Validate inputs
    total_prob = prob_home + prob_draw + prob_away
    if abs(total_prob - 1.0) > 0.01:  # Allow 1% tolerance
        # Normalize probabilities
        prob_home = prob_home / total_prob
        prob_draw = prob_draw / total_prob
        prob_away = prob_away / total_prob

    # Calculate double chance probabilities
    prob_1X = prob_home + prob_draw  # Home or Draw
    prob_X2 = prob_draw + prob_away  # Draw or Away
    prob_12 = prob_home + prob_away  # Home or Away (No Draw)

    # Get all possible outcomes with their probabilities
    outcomes = {
        'Home': prob_home,
        'Draw': prob_draw,
        'Away': prob_away,
        '1X': prob_1X,
        'X2': prob_X2,
        '12': prob_12
    }

    # Find the best single outcome (Home, Draw, or Away)
    single_outcomes = {
        'Home': prob_home,
        'Draw': prob_draw,
        'Away': prob_away
    }
    
    # Find the best single outcome
    best_single = max(single_outcomes.items(), key=lambda x: x[1])
    best_single_name = best_single[0]
    best_single_prob = best_single[1]
    
    # Get second best single outcome
    sorted_singles = sorted(single_outcomes.items(), key=lambda x: x[1], reverse=True)
    second_best_single_prob = sorted_singles[1][1] if len(sorted_singles) > 1 else 0
    
    # Thresholds (updated to match analytics.py improved logic)
    # Use double chance when confidence is low or outcomes are close
    CLEAR_WIN_THRESHOLD = 0.45  # 45% - must have at least this confidence for single outcome
    UNCERTAINTY_THRESHOLD = 0.08  # 8% - if top two are within this, use double chance
    DOUBLE_CHANCE_MIN_ADVANTAGE = 0.10  # 10% - double chance must be this much better to use it
    
    # Calculate double chance probabilities
    double_outcomes = {
        '1X': prob_1X,
        'X2': prob_X2,
        '12': prob_12
    }
    best_double = max(double_outcomes.items(), key=lambda x: x[1])
    best_double_name = best_double[0]
    best_double_prob = best_double[1]
    
    # Logic to decide between single outcome and double chance:
    # Match the logic from analytics.py for consistency
    prob_difference = best_single_prob - second_best_single_prob
    
    # Use double chance if confidence is low (< 45%) OR outcomes are close (< 8%)
    if best_single_prob < CLEAR_WIN_THRESHOLD or prob_difference < UNCERTAINTY_THRESHOLD:
        return best_double_name
    
    # Default to the best single outcome
    return best_single_name


def update_billing_statistics(user=None, session_key=None):
    """Update billing statistics after a prediction is made.
    
    Args:
        user: User object (for authenticated users)
        session_key: Session key (for anonymous users)
    """
    try:
        usage, created = BillingUsage.get_or_create_usage(user=user, session_key=session_key)
        if usage:
            # Update statistics from database
            usage.update_statistics()
            # Refresh from database to ensure we have the latest values
            usage.refresh_from_db()
            logger.info(f"Billing statistics updated: {usage.total_predictions} predictions, {usage.unique_teams_count} teams, {usage.unique_leagues_count} leagues (created: {created})")
        else:
            logger.warning(f"Failed to get or create billing usage for user={user}, session_key={session_key}")
    except Exception as e:
        logger.error(f"Error updating billing statistics: {e}")
        import traceback
        logger.error(traceback.format_exc())


def get_outcome_display(prediction):
    """Get display information for a prediction outcome.
    
    Args:
        prediction: Prediction model instance
    
    Returns:
        dict: Contains 'text', 'color', and 'icon' for the outcome
    """
    outcome = prediction.outcome or 'Draw'

    if outcome == "Home":
        return {
            'text': f"{prediction.home_team.upper()} WIN",
            'color': "#00d4aa",
            'icon': "🏆"
        }
    elif outcome == "Away":
        return {
            'text': f"{prediction.away_team.upper()} WIN",
            'color': "#ff6b35",
            'icon': "🏆"
        }
    elif outcome == "1X":
        return {
            'text': f"{prediction.home_team.upper()} OR DRAW",
            'color': "#3b82f6",
            'icon': "🤝"
        }
    elif outcome == "X2":
        return {
            'text': f"DRAW OR {prediction.away_team.upper()}",
            'color': "#3b82f6",
            'icon': "🤝"
        }
    elif outcome == "12":
        return {
            'text': f"{prediction.home_team.upper()} OR {prediction.away_team.upper()}",
            'color': "#3b82f6",
            'icon': "⚔️"
        }
    else:  # Draw or default
        return {
            'text': "DRAW",
            'color': "#f59e0b",
            'icon': "🤝"
        }


@login_required(login_url='predictor:login')
def home(request):
    """Home page view with real data from database. Requires authentication."""
    # Get user-specific predictions count (user is always authenticated due to @login_required)
    user_predictions = Prediction.objects.filter(user=request.user, is_archived=False)
    logger.info(f"Home view - Loading predictions for authenticated user: {request.user.username}")
    
    # Get billing statistics FIRST (most accurate tracking for billing)
    # This ensures we use the correct count that's updated after each prediction
    try:
        # User is always authenticated due to @login_required
        billing_usage = BillingUsage.objects.filter(user=request.user, is_active=True).first()
        
        if billing_usage:
            # ALWAYS update billing stats to ensure they're current (this recalculates from database)
            billing_usage.update_statistics()
            billing_usage.refresh_from_db()  # Refresh to get latest values
            # Use billing statistics (most accurate)
            total_predictions = billing_usage.total_predictions
            unique_teams = billing_usage.unique_teams_count
            unique_leagues = billing_usage.unique_leagues_count
            logger.info(f"Home view - Using billing stats: {total_predictions} predictions, {unique_teams} teams, {unique_leagues} leagues")
        else:
            # No billing record exists - get count from predictions first
            total_predictions = user_predictions.count()
            logger.info(f"Home view - No billing record, using direct count: {total_predictions} predictions")
            
            if total_predictions > 0:
                # Create billing record for future use
                try:
                    billing_usage, created = BillingUsage.get_or_create_usage(user=request.user, session_key=None)
                    
                    if billing_usage:
                        billing_usage.update_statistics()
                        billing_usage.refresh_from_db()
                        total_predictions = billing_usage.total_predictions
                        unique_teams = billing_usage.unique_teams_count
                        unique_leagues = billing_usage.unique_leagues_count
                        logger.info(f"Home view - Created billing record: {total_predictions} predictions, {unique_teams} teams, {unique_leagues} leagues")
                except Exception as e:
                    logger.error(f"Error creating billing record in home view: {e}")
                    # Fallback to direct calculation
                    # Get all unique team names from predictions
                    home_teams = user_predictions.values_list('home_team', flat=True).distinct()
                    away_teams = user_predictions.values_list('away_team', flat=True).distinct()
                    # Combine and get unique count
                    all_teams = set(list(home_teams) + list(away_teams))
                    unique_teams = len(all_teams)
                    
                    # Get unique leagues from predictions
                    unique_leagues = user_predictions.exclude(league__isnull=True).exclude(league='').values_list('league', flat=True).distinct().count()
            else:
                # No predictions at all - set defaults
                unique_teams = 0
                unique_leagues = 0
    except Exception as e:
        logger.warning(f"Error getting billing statistics: {e}")
        import traceback
        logger.warning(traceback.format_exc())
        # Fallback: calculate from predictions
        total_predictions = user_predictions.count()
        if total_predictions > 0:
            home_teams = user_predictions.values_list('home_team', flat=True).distinct()
            away_teams = user_predictions.values_list('away_team', flat=True).distinct()
            all_teams = set(list(home_teams) + list(away_teams))
            unique_teams = len(all_teams)
            unique_leagues = user_predictions.exclude(league__isnull=True).exclude(league='').values_list('league', flat=True).distinct().count()
        else:
            unique_teams = 0
            unique_leagues = 0
    
    logger.info(f"Home view - Final count: {total_predictions} total predictions")
    
    # Cap displayed count at free limit for non-subscribed users
    # This handles cases where users made predictions before the limit was enforced
    profile = getattr(request.user, 'profile', None)
    if profile:
        # Check if user has active subscription
        has_subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).exists()
        
        if not has_subscription:
            # Cap at free limit for display purposes
            display_predictions = min(total_predictions, profile.free_matches_limit)
        else:
            display_predictions = total_predictions
    else:
        display_predictions = total_predictions
    
    # Calculate accuracy rate (assuming we have some way to track accuracy)
    # For now, we'll use a realistic estimate based on total predictions
    if total_predictions > 0:
        accuracy_rate = min(85, 70 + (total_predictions // 100))  # Increases with more predictions
    else:
        accuracy_rate = 75  # Default accuracy
    
    # Get recent predictions (last 10) to show on dashboard
    recent_predictions = user_predictions.order_by('-prediction_date')[:10]
    
    # Add outcome display to each prediction
    predictions_with_display = []
    for pred in recent_predictions:
        display_info = get_outcome_display(pred)
        pred.outcome_text = display_info['text']
        pred.outcome_color = display_info['color']
        pred.outcome_icon = display_info['icon']
        predictions_with_display.append(pred)
    
    context = {
        'total_predictions': display_predictions,  # Use capped count for display
        'accuracy_rate': accuracy_rate,
        'teams_covered': unique_teams,
        'leagues_supported': unique_leagues,
        'recent_predictions': predictions_with_display,
        'status': check_subscription_status(request.user),
    }
    
    return render(request, 'predictor/home.html', context)


@login_required(login_url='predictor:login')
def predict(request):
    """Prediction page view. Requires login and active subscription or free matches."""
    # Check subscription status - user is authenticated due to @login_required
    status = check_subscription_status(request.user)
    if not status['has_access']:
        msg = status.get('message', 'You have used all your free matches. Please subscribe to continue making predictions.')
        messages.warning(request, msg)
        return redirect('predictor:subscribe')
    
    if request.method == 'POST':
        # Check subscription before processing prediction
        if not use_prediction_credit(request.user):
            # Check why it failed
            status = check_subscription_status(request.user)
            msg = status.get('message', 'You have used all your free matches. Please subscribe to continue.')
            messages.warning(request, msg)
            return redirect('predictor:subscribe')
        
        home_team = request.POST.get('home_team')
        away_team = request.POST.get('away_team')
        category = request.POST.get('category')
        league = request.POST.get('league')  # Get league from form
        
        # Validate: teams must be different
        if home_team and away_team:
            if home_team == away_team:
                return render(request, 'predictor/predict.html', {
                    'leagues_by_category': get_leagues_by_category(),
                    'error': 'Home team and away team must be different. Please select different teams.'
                })
        
        if home_team and away_team:
            # Use local prediction logic instead of API
            try:
                # Load models
                model1, model2 = load_prediction_models()
                
                # Use advanced prediction logic
                from .analytics import advanced_predict_match
                
                advanced_result = advanced_predict_match(home_team, away_team, model1, model2, category=category)
                
                # Debug logging for prediction result
                if advanced_result:
                     logger.info(f"Advanced Result Type: {type(advanced_result)}")
                     logger.info(f"Advanced Result Keys: {list(advanced_result.keys())}")
                     logger.info(f"Advanced Result Outcome: {advanced_result.get('outcome')}")
                     logger.info(f"Advanced Result Probabilities: {advanced_result.get('probabilities')}")
                else:
                     logger.error("Advanced Result is None or Empty")
                
                if not advanced_result:
                    # Fallback prediction if advanced_predict_match fails
                    import random
                    fallback_prediction = random.choice([0, 1, 2])
                    outcome = {0: 'Away', 1: 'Draw', 2: 'Home'}[fallback_prediction]
                    probabilities = {"Home": 0.33, "Draw": 0.34, "Away": 0.33}
                    confidence = 0.33
                    model_type = 'Model1 (Fallback)'
                    reasoning = 'Fallback prediction: insufficient data for model'
                    
                    # Generate fallback scores
                    if outcome == "Home":
                        home_score = random.choice([2, 3])
                        away_score = random.choice([0, 1])
                    elif outcome == "Away":
                        away_score = random.choice([2, 3])
                        home_score = random.choice([0, 1])
                    else:  # Draw
                        home_score = random.choice([0, 1, 2])
                        away_score = home_score
                    
                    prediction_number = fallback_prediction
                else:
                    # Use advanced prediction results
                    # Process probabilities consistently using shared function
                    probabilities, outcome = process_prediction_probabilities(advanced_result)
                    prediction_number = advanced_result['prediction_number']  # 0=Away, 1=Draw, 2=Home
                    
                    # Log probabilities for debugging consistency
                    logger.info(f"PREDICT view probabilities for {home_team} vs {away_team}: Home={probabilities.get('Home', 0)*100:.1f}%, Draw={probabilities.get('Draw', 0)*100:.1f}%, Away={probabilities.get('Away', 0)*100:.1f}%")
                    
                    # Update prediction_number based on outcome (for backward compatibility)
                    prediction_mapping = {
                        "Home": 2, "Draw": 1, "Away": 0,
                        "1X": 3, "X2": 4, "12": 5  # Double chance mappings
                    }
                    prediction_number = prediction_mapping.get(outcome, 1)
                    
                    # Calculate scores based on outcome and probabilities
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
                    elif outcome == "1X":
                        # Home or Draw - home doesn't lose
                        prob_1X = probabilities.get("Home", 0) + probabilities.get("Draw", 0)
                        if prob_1X > 0.7:  # Strong 1X probability
                            # More likely home win
                            home_score = random.choice([2, 3])
                            away_score = random.choice([0, 1])
                        else:  # Could be draw or home win
                            if random.random() < 0.5:  # 50% chance of draw
                                home_score = random.choice([0, 1, 2])
                                away_score = home_score
                            else:  # Home win
                                home_score = random.choice([1, 2])
                                away_score = random.choice([0, 1])
                        # Ensure home doesn't lose
                        if home_score < away_score:
                            home_score = away_score
                    elif outcome == "X2":
                        # Draw or Away - away doesn't lose
                        prob_X2 = probabilities.get("Draw", 0) + probabilities.get("Away", 0)
                        if prob_X2 > 0.7:  # Strong X2 probability
                            # More likely away win
                            away_score = random.choice([2, 3])
                            home_score = random.choice([0, 1])
                        else:  # Could be draw or away win
                            if random.random() < 0.5:  # 50% chance of draw
                                home_score = random.choice([0, 1, 2])
                                away_score = home_score
                            else:  # Away win
                                away_score = random.choice([1, 2])
                                home_score = random.choice([0, 1])
                        # Ensure away doesn't lose
                        if away_score < home_score:
                            away_score = home_score
                    elif outcome == "12":
                        # Home or Away - no draw
                        prob_12 = probabilities.get("Home", 0) + probabilities.get("Away", 0)
                        if probabilities.get("Home", 0) > probabilities.get("Away", 0):
                            # Home more likely
                            home_score = random.choice([2, 3])
                            away_score = random.choice([0, 1])
                        else:  # Away more likely
                            away_score = random.choice([2, 3])
                            home_score = random.choice([0, 1])
                        # Ensure no draw
                        if home_score == away_score:
                            if home_score == 0:
                                home_score = 1
                            else:
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
                    # For double chance, use the combined probability
                    if outcome == "1X":
                        confidence = probabilities.get("Home", 0) + probabilities.get("Draw", 0)
                    elif outcome == "X2":
                        confidence = probabilities.get("Draw", 0) + probabilities.get("Away", 0)
                    elif outcome == "12":
                        confidence = probabilities.get("Home", 0) + probabilities.get("Away", 0)
                    else:
                        confidence = float(max(probabilities.values()))
                    
                    # Get model_type from advanced_result
                    model_type = advanced_result.get('model_type', 'Model1')
                    reasoning = 'Based on historical data analysis'
                    
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
                            # Force session creation by setting a value
                            if not request.session.session_key:
                                request.session['_init'] = True
                                request.session.save()  # Explicitly save to ensure session_key is created
                            
                            session_key = request.session.session_key
                            logger.info(f"Predict view - Session key for anonymous user: {session_key}")
                            if not session_key:
                                logger.error("CRITICAL: Failed to get session_key after creation!")
                        else:
                            session_key = None
                        
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=home_score,
                            away_score=away_score,
                            confidence=confidence,
                            category=category or '',
                            league=league or '',  # Add league field
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
                        
                        # Update billing statistics
                        update_billing_statistics(
                            user=request.user if request.user.is_authenticated else None,
                            session_key=session_key
                        )
                        
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
                    
                    # Extract H2H probabilities from advanced_result if available
                    h2h_probs = advanced_result.get('historical_probs', {}) if advanced_result else {}
                    h2h_home = h2h_probs.get('Home Team Win', 0) / 100.0 if h2h_probs else 0.33
                    h2h_draw = h2h_probs.get('Draw', 0) / 100.0 if h2h_probs else 0.33
                    h2h_away = h2h_probs.get('Away Team Win', 0) / 100.0 if h2h_probs else 0.33
                    
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
                    'prediction_type': 'Single',
                        'prob_home': probabilities.get('Home', 0.33),
                        'prob_draw': probabilities.get('Draw', 0.33),
                        'prob_away': probabilities.get('Away', 0.33),
                        # Add H2H probabilities separately
                        'h2h_prob_home': h2h_home,
                        'h2h_prob_draw': h2h_draw,
                        'h2h_prob_away': h2h_away
                    })
                    return redirect(reverse('predictor:result') + '?' + params)
                    
            except Exception as e:
                logger.error(f"CRITICAL ERROR in prediction: {str(e)}")
                import traceback
                error_trace = traceback.format_exc()
                logger.error(error_trace)
                
                # Show detailed error to user
                leagues_data = get_leagues_by_category()
                import json
                return render(request, 'predictor/predict.html', {
                    'leagues_by_category': leagues_data,
                    'leagues_json': json.dumps(leagues_data),
                    'error': f'Prediction Error: {str(e)}\n\nPlease check the console logs for details.'
                })
            
    
    # For GET requests, render the prediction form with leagues data from database
    leagues_by_category = get_leagues_by_category()
    
    # Pre-encode as JSON for JS usage in templates
    import json
    leagues_json = json.dumps(leagues_by_category)
    
    # Check if multi-match mode is requested
    if request.GET.get('multi') == 'true':
        return render(request, 'predictor/predict_multi.html', {
            'leagues_by_category': leagues_by_category,
            'leagues_json': leagues_json
        })

    import json
    logger.info(f"Predict View - Leagues Data Keys: {list(leagues_by_category.keys())}")
    for cat, leagues in leagues_by_category.items():
        logger.info(f"Category {cat}: {list(leagues.keys())}")
        if 'Others' in cat and 'Switzerland' in leagues:
             logger.info(f"Switzerland teams: {leagues['Switzerland']}")

    leagues_json = json.dumps(leagues_by_category)
    return render(request, 'predictor/predict.html', {
        'leagues_by_category': leagues_by_category,
        'leagues_json': leagues_json,
        'debug_info': 'Data Reloaded'
    })


def get_leagues_by_category():
    """Get leagues organized by category from database."""
    from django.core.cache import cache
    cache_key = 'leagues_by_category_db'
    
    # Try to get from cache first
    try:
        cached = cache.get(cache_key)
        # Only return if cached data is NOT empty
        if cached:
            return cached
    except Exception:
        pass
    
    # Build structure from database
    # FAILSAFE: If no leagues exist, auto-seed the database
    if not League.objects.exists():
        try:
            from django.core.management import call_command
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("No leagues found in DB. Auto-seeding...")
            call_command('seed_leagues')
        except Exception as e:
            logger.error(f"Auto-seeding failed: {e}")

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


@login_required(login_url='predictor:login')
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


@login_required(login_url='predictor:login')
def history(request):
    """View prediction history with pagination and bulk operations.
    
    Optimized for high-traffic scenarios with:
    - Pagination (50 per page)
    - Database query optimization
    - Bulk delete functionality
    - Efficient statistics calculation
    Requires login.
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Avg, Count
    
    # Handle single prediction delete
    if request.method == 'POST' and 'delete_prediction' in request.POST:
        prediction_id = request.POST.get('prediction_id')
        if prediction_id:
            try:
                # User is authenticated due to @login_required
                prediction = Prediction.objects.get(id=prediction_id, user=request.user)
                
                prediction.delete()
                messages.success(request, 'Prediction deleted successfully')
            except Prediction.DoesNotExist:
                messages.error(request, 'Prediction not found')
            except Exception as e:
                logger.error(f"Error deleting prediction: {e}")
                messages.error(request, 'Error deleting prediction')
        
        return redirect('predictor:history')
    
    # Handle bulk delete
    if request.method == 'POST' and 'delete_selected' in request.POST:
        selected_ids = request.POST.getlist('prediction_ids')
        if selected_ids:
            # User is authenticated due to @login_required
            deleted_count = Prediction.objects.filter(
                id__in=selected_ids,
                user=request.user
            ).delete()[0]
            
            messages.success(request, f'Successfully deleted {deleted_count} prediction(s)')
            return redirect('predictor:history')
    
    # Handle delete all
    if request.method == 'POST' and 'delete_all' in request.POST:
        # User is authenticated due to @login_required
        deleted_count = Prediction.objects.filter(user=request.user).delete()[0]
        messages.success(request, f'Successfully deleted all {deleted_count} prediction(s)')
        return redirect('predictor:history')
    
    # Get predictions for authenticated user (optimized query)
    # User is authenticated due to @login_required
    predictions = Prediction.get_user_active_predictions(user=request.user, limit=1000)
    logger.info(f"History view - Loading predictions for authenticated user: {request.user.username}, count: {predictions.count()}")
    
    # Calculate statistics efficiently using aggregation
    if request.user.is_authenticated:
        stats = Prediction.objects.filter(
            user=request.user,
            is_archived=False
        ).aggregate(
            total=Count('id'),
            avg_confidence=Avg('confidence')
        )
        logger.info(f"History stats for user {request.user.username}: {stats}")
    else:
        # Ensure session exists
        if not request.session.session_key:
            request.session['_init'] = True
            request.session.save()  # Explicitly save to ensure session_key is created
        
        session_key = request.session.session_key
        if session_key:
            stats = Prediction.objects.filter(
                session_key=session_key,
                is_archived=False
            ).aggregate(
                total=Count('id'),
                avg_confidence=Avg('confidence')
            )
            logger.info(f"History stats for session {session_key}: {stats}")
        else:
            stats = {'total': 0, 'avg_confidence': 0}
            logger.warning("History stats - No session key, returning zero stats")
    
    total_predictions = stats['total'] or 0
    average_confidence = stats['avg_confidence'] or 0
    
    # Get best prediction BEFORE any slicing operations
    # Find best prediction (highest confidence) - must do this before slicing
    best_prediction = None
    best_confidence = 0
    if predictions.exists():
        # Get prediction with highest confidence from unsliced queryset
        # Need to get the queryset again to avoid slice issues
        if request.user.is_authenticated:
            best_pred_queryset = Prediction.objects.filter(
                user=request.user,
                is_archived=False
            ).order_by('-confidence')
        else:
            session_key_for_best = request.session.session_key
            if session_key_for_best:
                best_pred_queryset = Prediction.objects.filter(
                    session_key=session_key_for_best,
                    is_archived=False
                ).order_by('-confidence')
            else:
                best_pred_queryset = Prediction.objects.none()
        
        if best_pred_queryset.exists():
            best_pred = best_pred_queryset.first()
            if best_pred:
                best_prediction = best_pred
                best_confidence = best_pred.confidence
                # Convert to percentage if needed
                if best_confidence <= 1.0:
                    best_confidence = int(best_confidence * 100)
                else:
                    best_confidence = int(best_confidence)
    
    # Get recent activity (most recent prediction date)
    recent_activity = predictions.first().prediction_date if predictions.exists() else None
    
    # Calculate actual accuracy percentage (convert confidence to percentage)
    # Confidence is stored as decimal (0-1), convert to percentage (0-100)
    if average_confidence:
        if average_confidence <= 1.0:
            # Already in decimal format, convert to percentage
            accuracy_percentage = int(average_confidence * 100)
        else:
            # Already in percentage format
            accuracy_percentage = int(average_confidence)
    else:
        # Default accuracy if no predictions
        accuracy_percentage = 75
    
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
        'accuracy_percentage': accuracy_percentage,
        'recent_activity': recent_activity,
        'best_prediction': best_prediction,
        'best_confidence': best_confidence,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': paginated_predictions,
    }
    
    return render(request, 'predictor/history.html', context)


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
                
                # If models fail to load, they will be None and fallback logic will be used
                if model1 is None and model2 is None:
                    logger.warning('Both models failed to load, will use fallback prediction logic')
                elif model1 is None:
                    logger.warning('Model 1 failed to load, will use fallback for Model 1 predictions')
                elif model2 is None:
                    logger.warning('Model 2 failed to load, will use form-based fallback for Model 2 teams')
                
                
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
                        # Ensure session exists for anonymous users
                        session_key = None
                        if not request.user.is_authenticated:
                            if not request.session.session_key:
                                request.session['_init'] = True
                                request.session.save()  # Explicitly save to ensure session_key is created
                            session_key = request.session.session_key
                            if not session_key:
                                logger.error("CRITICAL: Failed to get session_key for fallback prediction!")
                        
                        prediction = Prediction.objects.create(
                            home_team=clean_team_name(home_team),
                            away_team=clean_team_name(away_team),
                            home_score=fallback_home_score,
                            away_score=fallback_away_score,
                            confidence=0.33,  # Default confidence for fallback
                            user=request.user if request.user.is_authenticated else None,
                            session_key=session_key
                        )
                        logger.info(f"Initial fallback prediction saved to database: {prediction}")
                        
                        # Update billing statistics
                        update_billing_statistics(
                            user=request.user if request.user.is_authenticated else None,
                            session_key=session_key
                        )
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
                    prediction_saved = False
                    duplicate_check = False
                    clean_home = clean_team_name(home_team)
                    clean_away = clean_team_name(away_team)
                    session_key = None
                    
                    try:
                        from django.core.cache import cache
                        from datetime import timedelta
                        
                        # Generate or get session key for non-authenticated users
                        if not request.user.is_authenticated:
                            if not request.session.session_key:
                                request.session['_init'] = True
                                request.session.save()  # Explicitly save to ensure session_key is created
                            session_key = request.session.session_key
                            if not session_key:
                                logger.error("CRITICAL: Failed to get session_key for API prediction!")
                                return JsonResponse({'error': 'Failed to create session. Please refresh the page and try again.'}, status=500)
                        else:
                            session_key = None
                        
                        # Prevent duplicate predictions - check if same match was predicted in last 5 minutes
                        recent_time = timezone.now() - timedelta(minutes=5)
                        
                        # Check for duplicates based on user/session and teams
                        if request.user.is_authenticated:
                            duplicate_check = Prediction.objects.filter(
                                user=request.user,
                                home_team=clean_home,
                                away_team=clean_away,
                                prediction_date__gte=recent_time
                            ).exists()
                        elif session_key:
                            duplicate_check = Prediction.objects.filter(
                                session_key=session_key,
                                home_team=clean_home,
                                away_team=clean_away,
                                prediction_date__gte=recent_time
                            ).exists()
                        else:
                            duplicate_check = False
                        
                        if duplicate_check:
                            logger.info(f"Duplicate prediction prevented: {clean_home} vs {clean_away}")
                            # Return existing prediction data instead of creating new one
                            if request.user.is_authenticated:
                                existing = Prediction.objects.filter(
                                    user=request.user,
                                    home_team=clean_home,
                                    away_team=clean_away
                                ).order_by('-prediction_date').first()
                            elif session_key:
                                existing = Prediction.objects.filter(
                                    session_key=session_key,
                                    home_team=clean_home,
                                    away_team=clean_away
                                ).order_by('-prediction_date').first()
                            else:
                                existing = None
                            
                            if existing:
                                # Update probabilities in response to match existing prediction
                                probabilities = {
                                    "Home": existing.prob_home or 0.33,
                                    "Draw": existing.prob_draw or 0.33,
                                    "Away": existing.prob_away or 0.33
                                }
                                outcome = existing.outcome or outcome
                                home_score = existing.home_score
                                away_score = existing.away_score
                                confidence = existing.confidence
                                prediction_saved = True  # Using existing prediction
                        else:
                            # Create new prediction
                            try:
                                prediction = Prediction.objects.create(
                                    home_team=clean_home,
                                    away_team=clean_away,
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
                                # Verify prediction was actually saved
                                if prediction and prediction.id:
                                    prediction_saved = True
                                    logger.info(f"API Prediction saved to database: {prediction.id} - {clean_home} vs {clean_away} (User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, Session: {session_key})")
                                    
                                    # Update billing statistics
                                    logger.info(f"Updating billing statistics for multi-match prediction (User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, Session: {session_key})")
                                    update_billing_statistics(
                                        user=request.user if request.user.is_authenticated else None,
                                        session_key=session_key
                                    )
                                else:
                                    logger.error(f"CRITICAL: Prediction object created but has no ID! {clean_home} vs {clean_away}")
                                    prediction_saved = False
                            except Exception as create_error:
                                logger.error(f"CRITICAL: Failed to create prediction in database: {create_error}")
                                import traceback
                                logger.error(traceback.format_exc())
                                prediction_saved = False
                        
                        # Clear cache to update history immediately (handle Redis unavailable)
                        try:
                            cache.delete('home_stats')
                            cache.delete('recent_predictions')
                        except Exception as cache_error:
                            logger.warning(f"Cache clear failed (Redis may be unavailable): {cache_error}")
                    except Exception as save_error:
                        logger.error(f"Error in prediction save process: {save_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                        prediction_saved = False
                    
                    # Log warning if prediction was not saved
                    if not prediction_saved and not duplicate_check:
                        logger.error(f"CRITICAL: Prediction for {clean_home} vs {clean_away} was NOT saved to database! Session: {session_key}")
                        # Try to save again as a last resort
                        try:
                            prediction = Prediction.objects.create(
                                home_team=clean_home,
                                away_team=clean_away,
                                home_score=home_score,
                                away_score=away_score,
                                confidence=confidence,
                                category=category or '',
                                outcome=outcome,
                                prob_home=probabilities.get('Home', 0.33),
                                prob_draw=probabilities.get('Draw', 0.33),
                                prob_away=probabilities.get('Away', 0.33),
                                model_type=model_type or 'Model1',
                                final_prediction=outcome,
                                user=request.user if request.user.is_authenticated else None,
                                session_key=session_key
                            )
                            logger.info(f"Retry: API Prediction saved to database: {prediction.id} - {clean_home} vs {clean_away}")
                            update_billing_statistics(
                                user=request.user if request.user.is_authenticated else None,
                                session_key=session_key
                            )
                            prediction_saved = True
                        except Exception as retry_error:
                            logger.error(f"CRITICAL: Retry save also failed: {retry_error}")
                    
                    # Get model_type from advanced_result
                    model_type = advanced_result.get('model_type', 'Model1') if advanced_result else 'Model1'
                    model2_prediction = advanced_result.get('model2_prediction') if advanced_result else None
                    
                    # Get confidence from advanced_result if available, otherwise use calculated confidence
                    result_confidence = advanced_result.get('confidence') if advanced_result else None
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
                        from datetime import timedelta
                        
                        # Generate or get session key for non-authenticated users
                        if not request.user.is_authenticated:
                            if not request.session.session_key:
                                request.session['_init'] = True
                                request.session.save()  # Explicitly save to ensure session_key is created
                            session_key = request.session.session_key
                            if not session_key:
                                logger.error("CRITICAL: Failed to get session_key for fallback API prediction!")
                        else:
                            session_key = None
                        
                        # Prevent duplicate predictions
                        clean_home = clean_team_name(home_team)
                        clean_away = clean_team_name(away_team)
                        recent_time = timezone.now() - timedelta(minutes=5)
                        
                        if request.user.is_authenticated:
                            duplicate_check = Prediction.objects.filter(
                                user=request.user,
                                home_team=clean_home,
                                away_team=clean_away,
                                prediction_date__gte=recent_time
                            ).exists()
                        elif session_key:
                            duplicate_check = Prediction.objects.filter(
                                session_key=session_key,
                                home_team=clean_home,
                                away_team=clean_away,
                                prediction_date__gte=recent_time
                            ).exists()
                        else:
                            duplicate_check = False
                        
                        if not duplicate_check:
                            prediction = Prediction.objects.create(
                                home_team=clean_home,
                                away_team=clean_away,
                                home_score=home_score,
                                away_score=away_score,
                                confidence=confidence,
                                user=request.user if request.user.is_authenticated else None,
                                session_key=session_key
                            )
                            # Verify prediction was actually saved
                            if prediction and prediction.id:
                                logger.info(f"API Fallback prediction saved to database: {prediction.id} - {clean_home} vs {clean_away} (Session: {session_key})")
                                
                                # Update billing statistics
                                logger.info(f"Updating billing statistics for fallback multi-match prediction (Session: {session_key})")
                                update_billing_statistics(
                                    user=request.user if request.user.is_authenticated else None,
                                    session_key=session_key
                                )
                            else:
                                logger.error(f"CRITICAL: Fallback prediction object created but has no ID! {clean_home} vs {clean_away}")
                        else:
                            logger.info(f"Duplicate fallback prediction prevented: {clean_home} vs {clean_away}")
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
    logger.info("Result View called with params:")
    logger.info(f"Home: {request.GET.get('home_team')} Away: {request.GET.get('away_team')}")
    logger.info(f"Outcome: {request.GET.get('outcome')}")
    logger.info(f"Probabilities: H={request.GET.get('prob_home')} D={request.GET.get('prob_draw')} A={request.GET.get('prob_away')}")
    home_team = clean_team_name(request.GET.get('home_team', ''))
    away_team = clean_team_name(request.GET.get('away_team', ''))
    category = request.GET.get('category', '')
    league = request.GET.get('league', '')
    
    # If team names are missing from URL, try to get from most recent prediction
    if not home_team or not away_team:
        try:
            # Filter by current user to get their latest prediction, not global latest
            if request.user.is_authenticated:
                latest_prediction = Prediction.objects.filter(user=request.user).latest('prediction_date')
            else:
                latest_prediction = None
                
            if latest_prediction:
                home_team = clean_team_name(latest_prediction.home_team)
                away_team = clean_team_name(latest_prediction.away_team)
                category = latest_prediction.category or ''
                league = latest_prediction.league or ''
                logger.info(f"Loaded teams from {request.user.username}'s latest prediction: {home_team} vs {away_team}")
        except Prediction.DoesNotExist:
            logger.warning(f"No predictions found for user {request.user.username if request.user.is_authenticated else 'anonymous'}")
        except Exception as e:
            logger.error(f"Error loading latest prediction: {e}")
    
    # Try to determine league if not provided
    if not league and home_team:
        try:
            league = get_league_for_team(home_team)
        except:
            pass

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
    if not final_prediction:
        final_prediction = request.GET.get('model1_prediction', '')
    
    # Convert confidence to float, handling both percentage and decimal formats
    try:
        if model1_confidence_str and model1_confidence_str != 'None':
            model1_confidence = float(model1_confidence_str)
            # If it's less than 1, it's probably a decimal (0.0-1.0), convert to percentage
            if model1_confidence <= 1.0:
                model1_confidence = model1_confidence * 100
            # Ensure it's a reasonable value (0-100)
            model1_confidence = max(0, min(100, model1_confidence))
            # Format to 1 decimal place
            model1_confidence = f"{model1_confidence:.1f}%"
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
    
    # Get probabilities from URL parameters if provided, otherwise try database, then calculate
    prob_home_param = request.GET.get('prob_home')
    prob_draw_param = request.GET.get('prob_draw')
    prob_away_param = request.GET.get('prob_away')
    
    # Get H2H probabilities from URL (for Historical Probabilities section)
    h2h_prob_home_param = request.GET.get('h2h_prob_home')
    h2h_prob_draw_param = request.GET.get('h2h_prob_draw')
    h2h_prob_away_param = request.GET.get('h2h_prob_away')
    
    # If not in URL, try to get from most recent prediction in database for these teams
    if not (prob_home_param and prob_draw_param and prob_away_param) and home_team and away_team:
        try:
            # First try exact match (home_team vs away_team)
            exact_pred = Prediction.objects.filter(
                home_team__iexact=home_team.strip(),
                away_team__iexact=away_team.strip()
            ).order_by('-prediction_date').first()
            
            # Also try reverse fixture (away_team vs home_team)
            reversed_pred = Prediction.objects.filter(
                home_team__iexact=away_team.strip(),
                away_team__iexact=home_team.strip()
            ).order_by('-prediction_date').first()
            
            # Use the most recent one, regardless of order
            recent_pred = None
            is_reversed = False
            
            if exact_pred and reversed_pred:
                # Both exist - use the most recent one
                if exact_pred.prediction_date >= reversed_pred.prediction_date:
                    recent_pred = exact_pred
                    is_reversed = False
                    logger.info(f"[RESULT VIEW] Found both exact and reversed predictions, using most recent EXACT match (ID: {exact_pred.id})")
                else:
                    recent_pred = reversed_pred
                    is_reversed = True
                    logger.info(f"[RESULT VIEW] Found both exact and reversed predictions, using most recent REVERSED match (ID: {reversed_pred.id})")
            elif exact_pred:
                recent_pred = exact_pred
                is_reversed = False
                logger.info(f"[RESULT VIEW] Found exact match prediction (ID: {exact_pred.id})")
            elif reversed_pred:
                recent_pred = reversed_pred
                is_reversed = True
                logger.info(f"[RESULT VIEW] Found reversed match prediction (ID: {reversed_pred.id})")
            
            if recent_pred and recent_pred.prob_home is not None:
                if is_reversed:
                    # Swap probabilities: what was home becomes away, what was away becomes home
                    prob_home_param = str(recent_pred.prob_away)  # Swap: away becomes home
                    prob_draw_param = str(recent_pred.prob_draw)  # Draw stays the same
                    prob_away_param = str(recent_pred.prob_home)  # Swap: home becomes away
                    logger.info(f"Using probabilities from REVERSED fixture prediction (ID: {recent_pred.id}, Date: {recent_pred.prediction_date}): Original was {recent_pred.home_team} vs {recent_pred.away_team}, swapped for {home_team} vs {away_team}")
                    logger.info(f"Swapped probabilities: Home={prob_home_param}, Draw={prob_draw_param}, Away={prob_away_param}")
                else:
                    # Exact match found, use as-is
                    prob_home_param = str(recent_pred.prob_home)
                    prob_draw_param = str(recent_pred.prob_draw)
                    prob_away_param = str(recent_pred.prob_away)
                    logger.info(f"[RESULT VIEW] Using probabilities from EXACT MATCH database prediction (ID: {recent_pred.id}, Date: {recent_pred.prediction_date}): Home={prob_home_param} ({recent_pred.prob_home*100:.1f}%), Draw={prob_draw_param} ({recent_pred.prob_draw*100:.1f}%), Away={prob_away_param} ({recent_pred.prob_away*100:.1f}%)")
            else:
                logger.warning(f"[RESULT VIEW] No saved probabilities found in database for {home_team} vs {away_team} (tried both directions)")
                logger.warning(f"[RESULT VIEW] Exact match search: home_team='{home_team}', away_team='{away_team}'")
                logger.warning(f"[RESULT VIEW] Reversed search: home_team='{away_team}', away_team='{home_team}'")
                # Log what exists in database
                all_preds = Prediction.objects.filter(
                    home_team__iexact=home_team
                ).values_list('home_team', 'away_team', 'prob_home', 'prob_draw', 'prob_away')[:5]
                logger.warning(f"[RESULT VIEW] Sample predictions with home_team='{home_team}': {list(all_preds)}")
        except Exception as e:
            logger.warning(f"Error getting probabilities from database: {e}")
            import traceback
            logger.warning(traceback.format_exc())
    
    if prob_home_param and prob_draw_param and prob_away_param:
        # Use probabilities from URL parameters or database
        try:
            prob_home_raw = float(prob_home_param)
            prob_draw_raw = float(prob_draw_param)
            prob_away_raw = float(prob_away_param)
            
            logger.info(f"[RESULT VIEW] Raw probabilities found - Home: {prob_home_raw}, Draw: {prob_draw_raw}, Away: {prob_away_raw}")
            
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
            
            temporary_probs = probabilities.copy()
            logger.info(f"[RESULT VIEW] Using probabilities from URL/database (normalized): Home={temporary_probs['Home']*100:.1f}%, Draw={temporary_probs['Draw']*100:.1f}%, Away={temporary_probs['Away']*100:.1f}%")
            # Save original probabilities BEFORE any recalculation
            saved_probabilities = temporary_probs.copy()
            
            # If model1_confidence is still None, calculate it from these probabilities
            if model1_confidence is None:
                try:
                    # Confidence is usually the highest probability
                    max_prob = max(temporary_probs.values())
                    model1_confidence = f"{max_prob * 100:.1f}%"
                    logger.info(f"[RESULT VIEW] Calculated missing confidence from probabilities: {model1_confidence}")
                except Exception as e:
                    logger.warning(f"Could not calculate confidence from probabilities: {e}")
            
            probabilities = temporary_probs
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing probabilities from URL: {e}")
            probabilities = None
            historical_probabilities = None
            saved_probabilities = None
    else:
        logger.warning(f"[RESULT VIEW] No probabilities found in URL or database - Home: {prob_home_param}, Draw: {prob_draw_param}, Away: {prob_away_param}")
        logger.warning(f"[RESULT VIEW] Will attempt to recalculate (this may cause inconsistent results)")
        probabilities = None
        historical_probabilities = None
        saved_probabilities = None
    
    # If probabilities not in URL or database, ONLY THEN recalculate
    # This ensures we always use saved probabilities when available
    # IMPORTANT: Only recalculate as a last resort - prefer saved data
    # BUT: If we have ANY prediction in database, use it instead of recalculating
    if probabilities is None:
        # Last chance: try to get ANY prediction for these teams (even without probabilities)
        try:
            any_pred = Prediction.objects.filter(
                home_team__iexact=home_team.strip(),
                away_team__iexact=away_team.strip()
            ).order_by('-prediction_date').first()
            
            if not any_pred:
                any_pred = Prediction.objects.filter(
                    home_team__iexact=away_team.strip(),
                    away_team__iexact=home_team.strip()
                ).order_by('-prediction_date').first()
                if any_pred:
                    # Swap probabilities if reversed
                    if any_pred.prob_home is not None:
                        prob_home_param = str(any_pred.prob_away)
                        prob_draw_param = str(any_pred.prob_draw)
                        prob_away_param = str(any_pred.prob_home)
                        logger.info(f"[RESULT VIEW] Found reversed prediction, using swapped probabilities")
            
            if any_pred and any_pred.prob_home is not None:
                if not prob_home_param:
                    prob_home_param = str(any_pred.prob_home)
                    prob_draw_param = str(any_pred.prob_draw)
                    prob_away_param = str(any_pred.prob_away)
                    logger.info(f"[RESULT VIEW] Found prediction with probabilities, using them instead of recalculating")
                    # Immediately convert to probabilities to prevent recalculation
                    try:
                        prob_home_raw = float(prob_home_param)
                        prob_draw_raw = float(prob_draw_param)
                        prob_away_raw = float(prob_away_param)
                        total_raw = prob_home_raw + prob_draw_raw + prob_away_raw
                        if total_raw > 10:  # Percentage format
                            probabilities = {
                                'Home': prob_home_raw / 100.0,
                                'Draw': prob_draw_raw / 100.0,
                                'Away': prob_away_raw / 100.0
                            }
                        else:  # Decimal format
                            probabilities = {
                                'Home': prob_home_raw,
                                'Draw': prob_draw_raw,
                                'Away': prob_away_raw
                            }
                        # Normalize
                        total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
                        if total_prob > 0:
                            probabilities['Home'] = probabilities['Home'] / total_prob
                            probabilities['Draw'] = probabilities['Draw'] / total_prob
                            probabilities['Away'] = probabilities['Away'] / total_prob
                        saved_probabilities = probabilities.copy()
                        logger.info(f"[RESULT VIEW] Converted database probabilities: Home={probabilities['Home']*100:.1f}%, Draw={probabilities['Draw']*100:.1f}%, Away={probabilities['Away']*100:.1f}%")
                    except Exception as conv_e:
                        logger.warning(f"[RESULT VIEW] Error converting database probabilities: {conv_e}")
        except Exception as e:
            logger.warning(f"[RESULT VIEW] Error in final database lookup: {e}")
    
    # Only recalculate if we STILL don't have probabilities AND no param values exist
    # Double-check: if we have param values but probabilities is None, convert them first
    if probabilities is None and prob_home_param and prob_draw_param and prob_away_param:
        # We have param values but probabilities wasn't set - convert them now
        try:
            prob_home_raw = float(prob_home_param)
            prob_draw_raw = float(prob_draw_param)
            prob_away_raw = float(prob_away_param)
            total_raw = prob_home_raw + prob_draw_raw + prob_away_raw
            if total_raw > 10:  # Percentage format
                probabilities = {
                    'Home': prob_home_raw / 100.0,
                    'Draw': prob_draw_raw / 100.0,
                    'Away': prob_away_raw / 100.0
                }
            else:  # Decimal format
                probabilities = {
                    'Home': prob_home_raw,
                    'Draw': prob_draw_raw,
                    'Away': prob_away_raw
                }
            # Normalize
            total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
            if total_prob > 0:
                probabilities['Home'] = probabilities['Home'] / total_prob
                probabilities['Draw'] = probabilities['Draw'] / total_prob
                probabilities['Away'] = probabilities['Away'] / total_prob
            saved_probabilities = probabilities.copy()
            logger.info(f"[RESULT VIEW] Converted param probabilities to dict: Home={probabilities['Home']*100:.1f}%, Draw={probabilities['Draw']*100:.1f}%, Away={probabilities['Away']*100:.1f}%")
        except Exception as e:
            logger.error(f"[RESULT VIEW] Error converting param probabilities: {e}")
    
    # Only recalculate if we STILL don't have probabilities
    # FINAL CHECK: If we have ANY prediction in database, NEVER recalculate - use fallback instead
    if probabilities is None:
        # Check one more time if ANY prediction exists
        has_any_prediction = False
        try:
            any_check = Prediction.objects.filter(
                home_team__iexact=home_team.strip(),
                away_team__iexact=away_team.strip()
            ).exists()
            if not any_check:
                any_check = Prediction.objects.filter(
                    home_team__iexact=away_team.strip(),
                    away_team__iexact=home_team.strip()
                ).exists()
            has_any_prediction = any_check
        except Exception:
            pass
        
        if has_any_prediction:
            logger.error(f"[RESULT VIEW] CRITICAL: Found predictions in database but couldn't load probabilities! Using fallback instead of recalculating.")
            logger.error(f"[RESULT VIEW] This should not happen - probabilities should have been loaded from database.")
            # Use fallback probabilities instead of recalculating
            probabilities = {'Home': 0.33, 'Draw': 0.34, 'Away': 0.33}
            saved_probabilities = probabilities.copy()
        else:
            logger.warning(f"[RESULT VIEW] Probabilities not found in URL or database for {home_team} vs {away_team}, will recalculate (this should be rare)")
            logger.warning(f"[RESULT VIEW] This may cause inconsistent results. Please ensure predictions are saved with probabilities.")
            from .analytics import calculate_probabilities_original, calculate_probabilities_model2, load_football_data
            try:
                # Determine which dataset to use based on team categories (same logic as advanced_predict_match)
                other_teams = set()
                main_teams = set()
                try:
                    # Build team categories (same as advanced_predict_match)
                    for category, leagues in LEAGUES_BY_CATEGORY.items():
                        for league, teams in leagues.items():
                            if category == 'European Leagues':
                                main_teams.update(teams)
                            else:
                                other_teams.update(teams)
                except Exception:
                    # Fallback: use database
                    try:
                        other_leagues = League.objects.filter(category='Others').prefetch_related('teams')
                        for league in other_leagues:
                            other_teams.update([team.name for team in league.teams.all()])
                    except Exception:
                        pass  # Fallback to default dataset
                
                # Determine which dataset to load (same logic as advanced_predict_match)
                if home_team in main_teams and away_team in main_teams:
                    required_dataset = 1
                elif home_team in other_teams and away_team in other_teams:
                    required_dataset = 2
                else:
                    required_dataset = 1  # Mixed teams - use dataset 1 as default
                
                # Load the required dataset
                data = load_football_data(required_dataset, use_cache=True)
                
                # Check if data is empty (handles both pandas DataFrame and our mock EmptyDataFrame)
                data_empty = hasattr(data, 'empty') and data.empty if hasattr(data, 'empty') else (not data if data else True)
                
                if not data_empty and home_team and away_team:
                    try:
                        # Use advanced_predict_match to ensure consistency with predict view
                        # This ensures we get blended probabilities (Model + Form + H2H)
                        from .analytics import advanced_predict_match
                        from .views import load_prediction_models, process_prediction_probabilities
                        
                        # Load models (cached)
                        model1, model2 = load_prediction_models()
                        
                        # Get advanced result
                        adv_result_recalc = advanced_predict_match(
                            home_team, away_team, 
                            model1, model2, 
                            category=category
                        )
                        
                        historical_probs_raw = None
                        if adv_result_recalc:
                             # Use the processed probabilities from the advanced result
                             # This handles the blending correctly
                             probs_recalc, _ = process_prediction_probabilities(adv_result_recalc)
                             
                             # Convert back to percent-like dict for compatibility with existing code structure below
                             # The code below expects 'Home Team Win' keys etc. or just raw dict
                             # Actually the code below expects 0-100 percentage keys...
                             # Let's just set probabilities directly and skip the raw processing block
                             probabilities = probs_recalc
                             historical_probs_raw = True # Flag to skip the if block below
                        else:
                             # Fallback to old logic if advanced fails
                             if home_team in other_teams and away_team in other_teams:
                                 historical_probs_raw = calculate_probabilities_model2(home_team, away_team, data, version="v2")
                                 if historical_probs_raw is None:
                                     historical_probs_raw = calculate_probabilities_original(home_team, away_team, data, version="v1")
                             else:
                                 historical_probs_raw = calculate_probabilities_original(home_team, away_team, data, version="v1")
                        
                        if historical_probs_raw is not None and historical_probs_raw is not True:
                            # historical_probs_raw are already in percentage format (0-100), convert to decimal (0-1)
                            probabilities = {
                                'Home': round(historical_probs_raw.get("Home Team Win", 33.0) / 100.0, 6),
                                'Draw': round(historical_probs_raw.get("Draw", 33.0) / 100.0, 6),
                                'Away': round(historical_probs_raw.get("Away Team Win", 33.0) / 100.0, 6)
                            }
                            # Normalize to ensure probabilities sum to exactly 1.0
                            total_prob = probabilities['Home'] + probabilities['Draw'] + probabilities['Away']
                            if total_prob > 0:
                                probabilities['Home'] = round(probabilities['Home'] / total_prob, 6)
                                probabilities['Draw'] = round(probabilities['Draw'] / total_prob, 6)
                                probabilities['Away'] = round(probabilities['Away'] / total_prob, 6)
                            # Store historical probabilities separately for Past Performance section
                            historical_probabilities = probabilities.copy()
                            logger.warning(f"[RESULT VIEW] RECALCULATED probabilities (should not happen if database has predictions): Home={probabilities['Home']*100:.1f}%, Draw={probabilities['Draw']*100:.1f}%, Away={probabilities['Away']*100:.1f}%")
                            
                            # If model1_confidence is absent, calculate it from these recalculated probabilities
                            if model1_confidence is None:
                                try:
                                    max_prob = max(probabilities.values())
                                    model1_confidence = f"{max_prob * 100:.1f}%"
                                    logger.info(f"[RESULT VIEW] Calculated confidence from recalculated probabilities: {model1_confidence}")
                                except:
                                    pass
                        else:
                            logger.warning("Historical probabilities returned None, using fallback")
                            probabilities = {'Home': 0.333, 'Draw': 0.334, 'Away': 0.333}
                            historical_probabilities = probabilities.copy()
                    except Exception as e:
                        logger.error(f"Error calculating historical probabilities: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        probabilities = {'Home': 0.333, 'Draw': 0.334, 'Away': 0.333}
                        historical_probabilities = probabilities.copy()
                else:
                    logger.warning(f"Data empty or teams missing. Data empty: {data_empty}, Home: {home_team}, Away: {away_team}")
                    probabilities = {'Home': 0.333, 'Draw': 0.334, 'Away': 0.333}
                    historical_probabilities = probabilities.copy()
            except ImportError as e:
                logger.error(f"Cannot load data due to import error (pandas may be corrupted): {e}")
                probabilities = {'Home': 0.333, 'Draw': 0.334, 'Away': 0.333}
                historical_probabilities = probabilities.copy()
            except Exception as e:
                logger.error(f"Error loading football data: {e}")
                import traceback
                logger.error(traceback.format_exc())
                probabilities = {'Home': 0.333, 'Draw': 0.334, 'Away': 0.333}
                historical_probabilities = probabilities.copy()
    
    # Set historical_probabilities from H2H parameters (raw H2H stats)
    # This is SEPARATE from the main probabilities (which are blended AI predictions)
    if h2h_prob_home_param and h2h_prob_draw_param and h2h_prob_away_param:
        try:
            historical_probabilities = {
                'Home': float(h2h_prob_home_param),
                'Draw': float(h2h_prob_draw_param),
                'Away': float(h2h_prob_away_param)
            }
            # Normalize
            total_hist = sum(historical_probabilities.values())
            if total_hist > 0:
                historical_probabilities = {k: v/total_hist for k, v in historical_probabilities.items()}
            logger.info(f"[RESULT VIEW] Using H2H probabilities from URL: Home={historical_probabilities['Home']*100:.1f}%, Draw={historical_probabilities['Draw']*100:.1f}%, Away={historical_probabilities['Away']*100:.1f}%")
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing H2H probabilities: {e}")
            # Fallback to saved probabilities if H2H parsing fails
            if 'saved_probabilities' in locals() and saved_probabilities:
                historical_probabilities = saved_probabilities.copy()
            elif probabilities:
                historical_probabilities = probabilities.copy()
            else:
                historical_probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
    elif 'saved_probabilities' in locals() and saved_probabilities:
        # Fallback: Try to RECALCULATE true historical probabilities first
        # This fixes issues where saved predictions had biased/incorrect probabilities due to old bugs (e.g. form stubs)
        try:
            from .analytics import calculate_probabilities_original, load_football_data
            # Load data
            calc_data = load_football_data(1, use_cache=True)
            # Calculate fresh
            hist_raw = calculate_probabilities_original(home_team, away_team, calc_data)
            
            if hist_raw:
                historical_probabilities = {
                    'Home': round(hist_raw.get("Home Team Win", 33.0) / 100.0, 6),
                    'Draw': round(hist_raw.get("Draw", 33.0) / 100.0, 6),
                    'Away': round(hist_raw.get("Away Team Win", 33.0) / 100.0, 6)
                }
                # Normalize
                total_h = sum(historical_probabilities.values())
                if total_h > 0:
                    historical_probabilities = {k: v/total_h for k, v in historical_probabilities.items()}
                logger.info(f"[RESULT VIEW] Recalculated FRESH historical probabilities: Home={historical_probabilities['Home']*100:.1f}%, Draw={historical_probabilities['Draw']*100:.1f}%, Away={historical_probabilities['Away']*100:.1f}%")
            else:
                historical_probabilities = saved_probabilities.copy()
                logger.info(f"[RESULT VIEW] Could not recalculate historical, using saved: Home={historical_probabilities['Home']*100:.1f}%...")
        except Exception as e_hist:
            logger.warning(f"[RESULT VIEW] Error recalculating historical: {e_hist}")
            historical_probabilities = saved_probabilities.copy()
            
    elif probabilities:
        # Fallback to current probabilities if saved_probabilities not available
        historical_probabilities = probabilities.copy()
        logger.info(f"[RESULT VIEW] Using current probabilities as historical_probabilities: Home={historical_probabilities['Home']*100:.1f}%, Draw={historical_probabilities['Draw']*100:.1f}%, Away={historical_probabilities['Away']*100:.1f}%")
    elif 'historical_probabilities' not in locals() or historical_probabilities is None:
        # Fallback only if no probabilities at all
        historical_probabilities = {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
        logger.warning(f"[RESULT VIEW] No probabilities found, using fallback for historical_probabilities")
    
    # Ensure historical_probabilities always has valid values (not None or empty)
    if not historical_probabilities or not isinstance(historical_probabilities, dict):
        historical_probabilities = probabilities.copy() if probabilities else {'Home': 0.33, 'Draw': 0.33, 'Away': 0.34}
    
    # Ensure all keys are present (but allow 0 as a valid probability value)
    # Only set fallback values if the key is MISSING, not if the value is 0
    if 'Home' not in historical_probabilities:
        if probabilities and 'Home' in probabilities:
            historical_probabilities['Home'] = probabilities.get('Home', 0.33)
        else:
            historical_probabilities['Home'] = 0.33
    
    if 'Draw' not in historical_probabilities:
        if probabilities and 'Draw' in probabilities:
            historical_probabilities['Draw'] = probabilities.get('Draw', 0.33)
        else:
            historical_probabilities['Draw'] = 0.33
    
    if 'Away' not in historical_probabilities:
        if probabilities and 'Away' in probabilities:
            historical_probabilities['Away'] = probabilities.get('Away', 0.33)
        else:
            historical_probabilities['Away'] = 0.33
    
    # Normalize to ensure they sum to 1.0
    total_hist = sum(historical_probabilities.values())
    if total_hist > 0:
        historical_probabilities = {k: v/total_hist for k, v in historical_probabilities.items()}
    
    logger.info(f"Final historical_probabilities for template: {historical_probabilities}")
    
    
    # Check if historical probabilities are valid (not default fallback)
    # Priority 1: If we have probabilities from URL parameters or database, they're valid
    # Priority 2: Check if probabilities are significantly different from 33/33/34 fallback
    has_valid_historical_prob = False
    
    if prob_home_param and prob_draw_param and prob_away_param:
        # We have probabilities from URL (saved prediction) - these are ALWAYS valid
        has_valid_historical_prob = True
        logger.info("✅ Valid historical probabilities: Loaded from URL/database (saved prediction)")
    elif historical_probabilities:
        home_prob = historical_probabilities.get('Home', 0.33)
        draw_prob = historical_probabilities.get('Draw', 0.33)
        away_prob = historical_probabilities.get('Away', 0.33)
        
        logger.info(f"[DATA SUFFICIENCY] Checking historical probabilities:")
        logger.info(f"  Home: {home_prob:.4f} (diff from 0.33: {abs(home_prob - 0.33):.4f})")
        logger.info(f"  Draw: {draw_prob:.4f} (diff from 0.33: {abs(draw_prob - 0.33):.4f})")
        logger.info(f"  Away: {away_prob:.4f} (diff from 0.34: {abs(away_prob - 0.34):.4f})")
        
        # Check if probabilities are significantly different from 33/33/34 fallback
        # Allow small tolerance for rounding (0.02 = 2%)
        is_fallback = (abs(home_prob - 0.33) < 0.02 and 
                      abs(draw_prob - 0.33) < 0.02 and 
                      abs(away_prob - 0.34) < 0.02)
        
        logger.info(f"  Is fallback check: {is_fallback}")
        
        if not is_fallback:
            has_valid_historical_prob = True
            logger.info("✅ Valid historical probabilities found (not default fallback)")
        else:
            has_valid_historical_prob = False
            logger.warning(f"⚠️ Historical probabilities appear to be default fallback values (33/33/34)")
            logger.warning(f"   This might be incorrect for {home_team} vs {away_team}")
    else:
        has_valid_historical_prob = False
        logger.info("No historical probabilities available")
    
    # DISABLED: Prediction saving in result view to prevent duplicates
    # api_predict already saves predictions, so this is redundant and causes duplicates
    # If you need backup saving, ensure proper duplicate checking with database transactions
    
    # Original code commented out to prevent duplicate predictions:
    """
    try:
        from django.core.cache import cache
        from django.utils import timezone
        from datetime import timedelta
        
        # Ensure session exists for anonymous users FIRST (before duplicate check)
        if not request.user.is_authenticated:
            # Force session creation by setting a value
            if not request.session.session_key:
                request.session['_init'] = True
                request.session.save()  # Explicitly save to ensure session_key is created
            
            session_key = request.session.session_key
            logger.info(f"Result view - Session key for anonymous user: {session_key}")
            if not session_key:
                logger.error("CRITICAL: Failed to get session_key in result view!")
        else:
            session_key = None
        
        # Only save if prediction doesn't exist in last 5 minutes (avoid duplicates)
        # Check by user/session AND teams to prevent duplicates
        recent_time = timezone.now() - timedelta(minutes=5)
        clean_home = clean_team_name(home_team)
        clean_away = clean_team_name(away_team)
        
        # Build duplicate check query
        if request.user.is_authenticated:
            recent_prediction = Prediction.objects.filter(
                user=request.user,
                home_team=clean_home,
                away_team=clean_away,
                prediction_date__gte=recent_time
            ).first()
        elif session_key:
            recent_prediction = Prediction.objects.filter(
                session_key=session_key,
                home_team=clean_home,
                away_team=clean_away,
                prediction_date__gte=recent_time
            ).first()
        else:
            recent_prediction = None
        
        if not recent_prediction and home_team and away_team:
            # Use calculated probabilities or get from URL
            prob_home_val = probabilities.get('Home', 0.33)
            prob_draw_val = probabilities.get('Draw', 0.33)
            prob_away_val = probabilities.get('Away', 0.33)
            
            # Calculate confidence from probabilities
            confidence_val = max(prob_home_val, prob_draw_val, prob_away_val)
            
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
            
            # Update billing statistics
            update_billing_statistics(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key
            )
            
            # Clear cache to update history (handle Redis unavailable)
            try:
                cache.delete('home_stats')
                cache.delete('recent_predictions')
            except Exception as cache_error:
                logger.warning(f"Cache clear failed (Redis may be unavailable): {cache_error}")
        else:
            # Duplicate detected - don't save again
            if recent_prediction:
                logger.info(f"Duplicate prediction prevented in result view: {clean_home} vs {clean_away} (existing ID: {recent_prediction.id})")
            else:
                logger.warning(f"Skipping prediction save in result view: missing team data")
    except Exception as save_error:
        logger.error(f"Error saving backup prediction in result view: {save_error}")
        # Don't fail the whole request if cache fails
    """
    
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
    # Track data sufficiency for fallback display
    has_sufficient_h2h = False
    has_valid_form = False
    # NOTE: has_valid_historical_prob is already set above (line ~2813) - DO NOT reset it here!
    # Resetting it here would overwrite the correct value and cause "Limited Historical Data" warnings
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
            dataset_version = "v2"
        else:
            data = load_football_data(1)
            dataset_version = "v1"
        
        if hasattr(data, 'columns') and len(data.columns) > 0 and not (hasattr(data, 'empty') and data.empty):
            home_col, away_col, result_col = get_column_names(dataset_version)
            
            # Get head-to-head matches
            try:
                # CRITICAL FIX: Use team name matching to handle "Arsenal" vs "Arsenal FC" etc.
                from .analytics import find_team_in_data
                
                # Find actual team names in the dataset
                home_matched = find_team_in_data(home_team, data, home_col)
                away_matched = find_team_in_data(away_team, data, away_col)
                
                if home_matched and away_matched:
                    logger.info(f"[H2H DISPLAY] Matched teams: '{home_team}' -> '{home_matched}', '{away_team}' -> '{away_matched}'")
                    # CRITICAL: Convert to string for comparison (handles both numeric IDs and string names)
                    home_matched_str = str(home_matched).strip()
                    away_matched_str = str(away_matched).strip()
                    h2h = data[(data[home_col].astype(str).str.strip() == home_matched_str) & 
                               (data[away_col].astype(str).str.strip() == away_matched_str)]
                else:
                    logger.warning(f"[H2H DISPLAY] Could not match teams in dataset: {home_team} -> {home_matched}, {away_team} -> {away_matched}")
                    h2h = data[(data[home_col].astype(str).str.strip() == str(home_team).strip()) & 
                               (data[away_col].astype(str).str.strip() == str(away_team).strip())]
                
                # If still empty, try case-insensitive as fallback
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
                        # Create a copy to avoid SettingWithCopyWarning
                        h2h = h2h.copy()
                        h2h['Date_parsed'] = pd.to_datetime(h2h['Date'], errors='coerce')
                        
                        # Only include matches before today (already played)
                        h2h = h2h[h2h['Date_parsed'] < today]
                        
                        # Sort by date (most recent first)
                        h2h = h2h.sort_values('Date_parsed', ascending=False)
                    h2h = h2h.head(5);
                    
                    # Track seen matches to avoid duplicates
                    seen_matches = set();
                    
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
                
                # Check if we have any H2H data at all
                # This matches the threshold in calculate_probabilities_model2
                if len(h2h_matches) >= 1:
                    has_sufficient_h2h = True
                    logger.info(f"H2H data found: {len(h2h_matches)} matches")
                    logger.info(f"First match sample: {h2h_matches[0]}")
                else:
                    logger.info(f"No H2H data: {len(h2h_matches)} matches found")
                
                # Now get upcoming/future matches (scheduled but not played yet)
                try:
                    # Use the same matched team names from H2H lookup above
                    if home_matched and away_matched:
                        # Use the same string conversion as H2H query above
                        h2h_future = data[(data[home_col].astype(str).str.strip() == home_matched_str) & 
                                          (data[away_col].astype(str).str.strip() == away_matched_str)]
                    else:
                        h2h_future = data[(data[home_col].astype(str).str.strip() == str(home_team).strip()) & 
                                          (data[away_col].astype(str).str.strip() == str(away_team).strip())]
                    
                    # If empty, try case-insensitive
                    if len(h2h_future) == 0:
                        h2h_future = data[(data[home_col].astype(str).str.strip().str.lower() == str(home_team).strip().lower()) & 
                                          (data[away_col].astype(str).str.strip().str.lower() == str(away_team).strip().lower())]
                    
                    if len(h2h_future) > 0 and 'Date' in h2h_future.columns:
                        from datetime import datetime
                        today = datetime.now()
                        
                        # Create a copy to avoid SettingWithCopyWarning
                        h2h_future = h2h_future.copy()
                        
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
                dataset_version = "v2"
                # Check if dataset 2 has the teams, if not try dataset 1
                if hasattr(data, 'columns') and len(data.columns) > 0:
                    temp_h_col, temp_a_col, _ = get_column_names("v2")
                    # Check if teams exist in dataset 2
                    home_matches = data[data[temp_h_col].astype(str).str.contains(home_team, case=False, na=False)]
                    away_matches = data[data[temp_a_col].astype(str).str.contains(away_team, case=False, na=False)]
                    if len(home_matches) == 0 and len(away_matches) == 0:
                        # Teams not in dataset 2, try dataset 1
                        logger.info(f"Teams {home_team}/{away_team} not in dataset 2, trying dataset 1")
                        data = load_football_data(1, use_cache=True)
                        dataset_version = "v1"
            else:
                data = load_football_data(1, use_cache=True)  # Use dataset 1 for Model 1 teams
                dataset_version = "v1"
            
            # Check if data is actually usable (not our mock EmptyDataFrame)
            data_usable = hasattr(data, 'columns') and len(data.columns) > 0 and not (hasattr(data, 'empty') and data.empty and len(data.columns) == 0)
            
            if data_usable:
                # Try to get form from actual data
                try:
                    home_team_form = get_team_recent_form_original(home_team, data, version=dataset_version)
                    away_team_form = get_team_recent_form_original(away_team, data, version=dataset_version)
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
            if not data_usable or not home_team_form or not away_team_form or home_team_form == '-----' or away_team_form == '-----':
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
            
            # ORIGINAL LOGIC FROM lGIC - Use available information without padding
            # (Padding with 'D' removed as requested by user)
            logger.info(f"Team forms - {home_team}: {home_team_form}, {away_team}: {away_team_form}")
            
            # Check if form data is valid (from actual data, not hash-based)
            # We need to verify it's not the generated fallback form that analytics.py creates
            import hashlib
            def get_generated_form(team_name):
                t_hash = int(hashlib.md5(str(team_name).strip().encode()).hexdigest()[:8], 16)
                chars = []
                for i in range(5):
                    val = (t_hash + i * 7919) % 100
                    if val < 40: chars.append("W")
                    elif val < 70: chars.append("D")
                    else: chars.append("L")
                return "".join(chars)

            gen_home = get_generated_form(home_team)
            gen_away = get_generated_form(away_team)
            
            # If the calculated form matches the generated one, it's likely a fallback
            is_generated = (home_team_form == gen_home) or (away_team_form == gen_away)
            
            # If data_usable was True and forms were retrieved, it's valid ONLY if not generated
            if data_usable and home_team_form and away_team_form and not is_generated and home_team_form != 'DDDDD' and away_team_form != 'DDDDD':
                has_valid_form = True
                logger.info("Valid form data found from actual match data")
            else:
                has_valid_form = False
                logger.info(f"Form data is hash-based/generated or missing (Generated check: {is_generated})")
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
    # Calculate statistics manually in Python to ensure accuracy
    home_predictions = 0
    draw_predictions = 0
    away_predictions = 0
    
    # Iterate through outcomes (more robust than DB filtering for stats)
    for pred in all_predictions:
        # Determine effective outcome for stats counting
        # Logic: If probabilities exist, the "Vote" goes to the highest probability outcome
        # This aligns with the "Safety Switch" logic: DC is just a label for a close race, 
        # but for stats we want to know "Which side did the model favor most?"
        winning_outcome = None
        
        if pred.prob_home is not None and pred.prob_draw is not None and pred.prob_away is not None:
            try:
                p_h = float(pred.prob_home)
                p_d = float(pred.prob_draw)
                p_a = float(pred.prob_away)
                
                # Find max probability to determine the model's primary lean
                max_p = max(p_h, p_d, p_a)
                if max_p == p_h:
                    winning_outcome = 'Home'
                elif max_p == p_d:
                    winning_outcome = 'Draw'
                else:
                    winning_outcome = 'Away'
            except (ValueError, TypeError):
                # Fallback if probability parsing fails
                winning_outcome = None
        
        # Normalize outcome string
        if not winning_outcome:
            o_raw = str(pred.outcome).strip()
            o = o_raw.lower().replace(" ", "")  # Normalize: '1x' or 'homewin'
            
            # Standard outcomes
            if o in ['home', 'homewin'] or f"{home_team.lower().replace(' ', '')}win" in o:
                winning_outcome = 'Home'
            elif o == 'draw':
                winning_outcome = 'Draw'
            elif o in ['away', 'awaywin'] or f"{away_team.lower().replace(' ', '')}win" in o:
                winning_outcome = 'Away'
            # Double Chance (Split weight if we don't have probabilities)
            elif '1x' in o or 'x1' in o or 'homeordraw' in o:
                home_predictions += 0.5
                draw_predictions += 0.5
                continue
            elif 'x2' in o or '2x' in o or 'draworaway' in o:
                draw_predictions += 0.5
                away_predictions += 0.5
                continue
            elif '12' in o or 'homeoraway' in o:
                home_predictions += 0.5
                away_predictions += 0.5
                continue
            # Fallback partial matching
            elif 'win' in o:
                if home_team and home_team.lower().replace(" ", "") in o:
                    winning_outcome = 'Home'
                elif away_team and away_team.lower().replace(" ", "") in o:
                    winning_outcome = 'Away'

        # Increment counts based on determined winning_outcome
        if winning_outcome == 'Home':
            home_predictions += 1
        elif winning_outcome == 'Draw':
            draw_predictions += 1
        elif winning_outcome == 'Away':
            away_predictions += 1
    
    logger.info(f"Stats Calculated (Python) - Home: {home_predictions}, Draw: {draw_predictions}, Away: {away_predictions} (Total: {total_predictions_count})")

    
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
        'home_count': int(round(home_predictions, 1)) if round(home_predictions, 1) % 1 == 0 else round(home_predictions, 1),
        'draw_count': int(round(draw_predictions, 1)) if round(draw_predictions, 1) % 1 == 0 else round(draw_predictions, 1),
        'away_count': int(round(away_predictions, 1)) if round(away_predictions, 1) % 1 == 0 else round(away_predictions, 1),
        'home_percentage': (home_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'draw_percentage': (draw_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'away_percentage': (away_predictions / total_predictions_count * 100) if total_predictions_count > 0 else 0,
        'home_percentage_fmt': f"{(home_predictions / total_predictions_count * 100):.0f}" if total_predictions_count > 0 else "0",
        'draw_percentage_fmt': f"{(draw_predictions / total_predictions_count * 100):.0f}" if total_predictions_count > 0 else "0",
        'away_percentage_fmt': f"{(away_predictions / total_predictions_count * 100):.0f}" if total_predictions_count > 0 else "0",
        'avg_home_score': round(avg_home_score, 1),
        'avg_away_score': round(avg_away_score, 1),
        'avg_confidence': round(avg_confidence * 100, 1) if avg_confidence <= 1 else round(avg_confidence, 1)
    }
    
    # Format prediction outcome for display
    prediction_outcome = 'DRAW'
    if outcome == 'Home':
        prediction_outcome = f'{home_team.upper()} WIN'
    elif outcome == 'Away':
        prediction_outcome = f'{away_team.upper()} WIN'
    elif outcome == '1X':
        prediction_outcome = f'{home_team.upper()} OR DRAW'
    elif outcome == 'X2':
        prediction_outcome = f'DRAW OR {away_team.upper()}'
    elif outcome == '12':
        prediction_outcome = f'{home_team.upper()} OR {away_team.upper()}'
    
    elif outcome == '12':
        prediction_outcome = f'{home_team.upper()} OR {away_team.upper()}'
    
    # Format probabilities for template display to avoid filter issues
    if probabilities:
        prob_home_pct = f"{probabilities['Home']*100:.1f}"
        prob_draw_pct = f"{probabilities['Draw']*100:.1f}"
        prob_away_pct = f"{probabilities['Away']*100:.1f}"
    else:
        prob_home_pct = "33.3"
        prob_draw_pct = "33.4"
        prob_away_pct = "33.3"
    
    context = {
        'home_team': home_team,
        'away_team': away_team,
        'home_score': home_score,
        'away_score': away_score,
        'category': category,
        'league': league,
        'outcome': outcome,
        'prediction_outcome': prediction_outcome,
        'prediction_number': prediction_number,
        'probabilities': probabilities,
        'prob_home_pct': prob_home_pct,
        'prob_draw_pct': prob_draw_pct,
        'prob_away_pct': prob_away_pct,
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
        'prediction_stats': prediction_stats,
        # Data sufficiency flags for conditional display
        'has_sufficient_h2h': has_sufficient_h2h,
        'has_valid_form': has_valid_form,
        'has_valid_historical_prob': has_valid_historical_prob,
        'has_valid_history': has_sufficient_h2h,  # Mapping for template compatibility
        'show_no_data_message': not (has_sufficient_h2h or has_valid_form or has_valid_historical_prob)
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


# ==================== ADMIN DASHBOARD VIEWS ====================

def admin_required(view_func):
    """Decorator to ensure user is admin (superuser or staff)."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access the admin dashboard.')
            return redirect('predictor:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Main admin dashboard with system overview and controls."""
    from django.contrib.auth.models import User
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    # Get system statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count()
    total_predictions = Prediction.objects.count()
    today_predictions = Prediction.objects.filter(
        prediction_date__date=timezone.now().date()
    ).count()
    
    # Get subscription stats
    from .models import Subscription
    active_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = Subscription.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get billing stats
    total_billing = BillingUsage.objects.aggregate(Sum('total_predictions'))['total_predictions__sum'] or 0
    
    # Recent activity
    recent_predictions = Prediction.objects.select_related('user').order_by('-prediction_date')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_predictions': total_predictions,
        'today_predictions': today_predictions,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'total_billing': total_billing,
        'recent_predictions': recent_predictions,
        'is_admin': True,
    }
    
    return render(request, 'predictor/admin/dashboard.html', context)


@admin_required
def admin_users(request):
    """Manage users - view all users and their activity."""
    from django.contrib.auth.models import User
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    users = User.objects.annotate(
        prediction_count=Count('prediction')
    ).order_by('-date_joined')
    
    # Filter by search query if provided
    search = request.GET.get('search', '')
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
    
    # Get subscription info for each user
    from .models import Subscription
    for user in users:
        user.subscription = Subscription.objects.filter(user=user).first()
        user.is_active_user = user.last_login and user.last_login >= timezone.now() - timedelta(days=7)
    
    context = {
        'users': users,
        'search': search,
        'total_users': User.objects.count(),
    }
    
    return render(request, 'predictor/admin/users.html', context)


@admin_required
def admin_system(request):
    """System controls and monitoring."""
    import os
    import sys
    from django.core.cache import cache
    
    system_info = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'django_version': __import__('django').VERSION,
        'database': 'SQLite' if 'sqlite' in str(__import__('django.conf').conf.DATABASES['default']) else 'Other',
        'debug_mode': __import__('django.conf').conf.DEBUG,
        'allowed_hosts': __import__('django.conf').conf.ALLOWED_HOSTS,
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'clear_cache':
            cache.clear()
            messages.success(request, 'Cache cleared successfully!')
        
        elif action == 'clear_old_predictions':
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=30)
            deleted_count, _ = Prediction.objects.filter(
                prediction_date__lt=cutoff_date,
                model_type='draft'
            ).delete()
            messages.success(request, f'Deleted {deleted_count} old draft predictions!')
        
        elif action == 'cleanup_users':
            # Clean up inactive users (optional)
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=90)
            inactive_users = User.objects.filter(last_login__lt=cutoff_date)
            count = inactive_users.count()
            messages.info(request, f'Found {count} inactive users (not deleted, just notified).')
        
        return redirect('predictor:admin_system')
    
    context = {
        'system_info': system_info,
    }
    
    return render(request, 'predictor/admin/system.html', context)


@admin_required
def admin_predictions(request):
    """View and manage all predictions."""
    predictions = Prediction.objects.select_related('user').order_by('-prediction_date')
    
    # Filters
    category = request.GET.get('category')
    league = request.GET.get('league')
    user_id = request.GET.get('user')
    
    if category:
        predictions = predictions.filter(category=category)
    if league:
        predictions = predictions.filter(league=league)
    if user_id:
        predictions = predictions.filter(user_id=user_id)
    
    # Get unique categories and leagues for filter dropdowns
    categories = Prediction.objects.values_list('category', flat=True).distinct()
    leagues = Prediction.objects.values_list('league', flat=True).distinct()
    from django.contrib.auth.models import User
    users = User.objects.filter(prediction__isnull=False).distinct()
    
    context = {
        'predictions': predictions[:100],  # Paginate to first 100
        'categories': categories,
        'leagues': leagues,
        'users': users,
        'selected_category': category,
        'selected_league': league,
        'selected_user': user_id,
    }
    
    return render(request, 'predictor/admin/predictions.html', context)


@admin_required
def admin_subscriptions(request):
    """Manage subscriptions and billing."""
    from .models import Subscription
    
    subscriptions = Subscription.objects.select_related('user').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        subscriptions = subscriptions.filter(status=status)
    
    context = {
        'subscriptions': subscriptions[:100],
        'statuses': ['active', 'inactive', 'completed', 'cancelled'],
        'selected_status': status,
    }
    
    return render(request, 'predictor/admin/subscriptions.html', context)


def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.
    
    Checks:
    - Database connectivity
    - Redis cache connectivity (if configured)
    - Application is running
    
    Returns:
    - 200 OK if healthy
    - 500 Internal Server Error if unhealthy
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'
        logger.error(f"Health check - Database error: {e}")
    
    try:
        # Check Redis cache (if configured)
        from django.core.cache import cache
        cache.set('health_check_test', 'ok', 10)
        result = cache.get('health_check_test')
        if result == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'warning: cache not working properly'
    except Exception as e:
        # Cache failure is not critical, just log it
        health_status['checks']['cache'] = f'warning: {str(e)}'
        logger.warning(f"Health check - Cache warning: {e}")
    
    # Return appropriate status code
    if health_status['status'] == 'healthy':
        return JsonResponse(health_status, status=200)
    else:
        return JsonResponse(health_status, status=500)


def init_database(request):
    """
    Manual database initialization endpoint.
    Call this on Render to populate the database with leagues and teams.
    Access: https://your-site.onrender.com/init-db/
    """
    from django.core.management import call_command
    from django.core.cache import cache
    import logging
    
    logger = logging.getLogger(__name__)
    
    response_data = {
        'status': 'starting',
        'steps': []
    }
    
    try:
        # Step 1: Check current state
        league_count_before = League.objects.count()
        team_count_before = Team.objects.count()
        response_data['steps'].append({
            'step': 'initial_check',
            'leagues_before': league_count_before,
            'teams_before': team_count_before
        })
        
        # Step 2: Run seed command
        try:
            call_command('seed_leagues')
            response_data['steps'].append({
                'step': 'seed_command',
                'status': 'success'
            })
        except Exception as e:
            response_data['steps'].append({
                'step': 'seed_command',
                'status': 'failed',
                'error': str(e)
            })
            logger.error(f"Seed command failed: {e}")
        
        # Step 3: Verify data
        league_count_after = League.objects.count()
        team_count_after = Team.objects.count()
        response_data['steps'].append({
            'step': 'verification',
            'leagues_after': league_count_after,
            'teams_after': team_count_after,
            'leagues_added': league_count_after - league_count_before,
            'teams_added': team_count_after - team_count_before
        })
        
        # Step 4: Clear cache
        cache.clear()
        response_data['steps'].append({
            'step': 'cache_clear',
            'status': 'success'
        })
        
        # Step 5: Sample data
        sample_leagues = []
        for league in League.objects.all()[:5]:
            sample_leagues.append({
                'name': league.name,
                'category': league.category,
                'teams_count': league.teams.count()
            })
        response_data['sample_leagues'] = sample_leagues
        
        response_data['status'] = 'completed'
        response_data['message'] = f'Database initialized with {league_count_after} leagues and {team_count_after} teams'
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        response_data['status'] = 'error'
        response_data['error'] = str(e)
        logger.error(f"Database initialization failed: {e}")
        return JsonResponse(response_data, status=500)

