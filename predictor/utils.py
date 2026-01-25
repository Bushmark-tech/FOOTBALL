import logging
import warnings
import sys

# Configure logging
logger = logging.getLogger(__name__)

def safe_import_pandas():
    """Safely import pandas."""
    try:
        import pandas as pd
        # Suppress pandas FutureWarning about downcasting
        warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")
        return pd
    except Exception as e:
        logger.error(f"Failed to import pandas: {e}")
        return None

def safe_import_numpy():
    """Safely import numpy."""
    try:
        import numpy as np
        return np
    except Exception as e:
        logger.error(f"Failed to import numpy: {e}")
        return None

def normalize_team_name(team_name):
    """
    Normalize common team name variations to their full official names.
    This fixes issues where "Man City" doesn't match "Manchester City" in the dataset.
    """
    if not team_name:
        return team_name
    
    # Common team name mappings (case-insensitive)
    name_mappings = {
        'man city': 'Man City',
        'manchester city': 'Man City',
        'man utd': 'Man United',
        'man united': 'Man United',
        'man u': 'Man United',
        'manu': 'Man United',
        'manchester united': 'Man United',
        'spurs': 'Tottenham',
        'tottenham hotspur': 'Tottenham',
        'wolves': 'Wolves',
        'wolverhampton wanderers': 'Wolves',
        'newcastle': 'Newcastle',
        'newcastle united': 'Newcastle',
        'west ham': 'West Ham',
        'west ham united': 'West Ham',
        'leicester': 'Leicester',
        'leicester city': 'Leicester',
        'brighton': 'Brighton',
        'brighton \u0026 hove albion': 'Brighton',
        'brighton and hove albion': 'Brighton',
        'nott\'m forest': 'Nott\'m Forest',
        'nottingham': 'Nott\'m Forest',
        'nottingham forest': 'Nott\'m Forest',
        'forest': 'Nott\'m Forest',
        'sheffield utd': 'Sheffield United',
        'sheffield united': 'Sheffield United',
        'sheffield wed': 'Sheffield Weds',
        'sheffield wednesday': 'Sheffield Weds',
        'west brom': 'West Brom',
        'west bromwich albion': 'West Brom',
        'wba': 'West Brom',
        'leeds': 'Leeds',
        'leeds united': 'Leeds',
        'aston villa': 'Aston Villa',
        'villa': 'Aston Villa',
        'st gallen': 'St. Gallen',
        'copenhagen': 'FC Copenhagen',
        'fc copenhagen': 'FC Copenhagen',
        'rb salzburg': 'Salzburg',
        'red bull salzburg': 'Salzburg',
        'rapid vienna': 'SK Rapid',
        'grasshopper': 'Grasshoppers',
        'grasshoppers': 'Grasshoppers',
        'young boys': 'Young Boys',
        'youngboys': 'Young Boys',
        'club america': 'Club America',
        'america': 'Club America',
    }
    
    try:
        team_lower = str(team_name).lower().strip()
        normalized = name_mappings.get(team_lower, team_name)
        # logger.debug(f"Normalized '{team_name}' -> '{normalized}'")
        return normalized
    except Exception:
        return team_name
