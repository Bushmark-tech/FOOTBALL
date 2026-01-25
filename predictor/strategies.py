from abc import ABC, abstractmethod
import logging
from .repositories import get_repository
from .utils import safe_import_numpy

logger = logging.getLogger(__name__)

class ProbabilityCalculator(ABC):
    """Base class for probability calculation strategies"""
    
    @abstractmethod
    def calculate(self, home_team, away_team, data, adapter):
        """
        Returns: dict with keys 'Home Team Win', 'Draw', 'Away Team Win'
                 or None if cannot calculate
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self):
        """For logging which strategy was used"""
        pass


class HistoricalH2HCalculator(ProbabilityCalculator):
    """Pure head-to-head historical data"""
    
    def calculate(self, home_team, away_team, data, adapter):
        repo = get_repository()
        result_col = adapter.get_result_column()
        
        # Get H2H matches (both directions) using repository
        h2h_home, h2h_away = repo.get_h2h_matches(home_team, away_team, data, adapter)
        
        total_len = len(h2h_home) + len(h2h_away)
        
        # Require minimum 3 matches for reliable historical probabilities
        # With only 1-2 matches, probabilities become too extreme (0% or 100%)
        MIN_H2H_MATCHES = 3
        
        if total_len < MIN_H2H_MATCHES:
            return None  # Insufficient H2H data - will show "Limited Historical Data" warning
        
        # Calculate with home advantage weighting
        # Direction 1: home_team was HOME. 
        # Direction 2: home_team was AWAY (reversed).
        
        # We need to count results normalized to "home win", "draw", "away win"
        # BUT relative to the *current* match where home_team is HOME.
        
        home_wins = 0.0
        draws = 0.0
        away_wins = 0.0
        
        total_weight = 0.0
        
        # Process matches where home_team was HOME (Direct matches)
        # Weight = 1.0 (Most relevant)
        if len(h2h_home) > 0:
            weight = 1.0
            for val in h2h_home[result_col]:
                normalized = adapter.normalize_result(val)
                # 0=Away, 1=Draw, 2=Home
                if normalized == 2:
                    home_wins += weight
                elif normalized == 1:
                    draws += weight
                elif normalized == 0:
                    away_wins += weight
                total_weight += weight

        # Process matches where home_team was AWAY (Reverse matches)
        # Weight = 0.6 (Less relevant because home advantage is flipped)
        # We need to flip the result perspective:
        # If home_team (Away in that match) won -> It corresponds to Away Win (0) in that match -> Our Home Win
        # Wait, let's trace:
        # In reverse match: home_team is AWAY.
        # If result is "Away Win" (0) -> It means home_team WON. So for our context (Home Team Win), we add points.
        # If result is "Home Win" (2) -> It means away_team WON. So for our context (Away Team Win), we add points.
        if len(h2h_away) > 0:
            weight = 0.6
            for val in h2h_away[result_col]:
                normalized = adapter.normalize_result(val)
                # 0=Away Win (home_team won), 1=Draw, 2=Home Win (away_team won)
                if normalized == 2: # Their Home won = Our Away Team won
                    away_wins += weight
                elif normalized == 1:
                    draws += weight
                elif normalized == 0: # Their Away won = Our Home Team won
                    home_wins += weight
                total_weight += weight
        
        if total_weight == 0:
            return None
            
        # Apply Laplace Smoothing to prevent 0% or 100% probabilities
        # Add a small buffer (1.0) to each outcome's weighted count
        # This adds 3.0 to the total_weight
        # Example: 9 wins out of 9 matches (100%) becomes 10/12 (83%)
        # This provides "realistic" uncertainty even for dominant teams
        SMOOTHING_FACTOR = 1.0
        
        smoothed_home = home_wins + SMOOTHING_FACTOR
        smoothed_draw = draws + SMOOTHING_FACTOR
        smoothed_away = away_wins + SMOOTHING_FACTOR
        
        smoothed_total = total_weight + (SMOOTHING_FACTOR * 3)
        
        logger.info(f"H2H {home_team} vs {away_team}: "
                   f"Weighted H:{home_wins:.1f} D:{draws:.1f} A:{away_wins:.1f} (matches={total_len}) - Smoothed to {smoothed_total:.1f}")
        
        return {
            "Home Team Win": (smoothed_home / smoothed_total) * 100,
            "Draw": (smoothed_draw / smoothed_total) * 100,
            "Away Team Win": (smoothed_away / smoothed_total) * 100
        }
    
    def get_strategy_name(self):
        return "Historical H2H"


class FormBasedCalculator(ProbabilityCalculator):
    """Based on recent team form (last 5 matches)"""
    
    def calculate(self, home_team, away_team, data, adapter):
        # We need to import analytics_engine to reuse strength calculation logic
        # To avoid circular imports, strict dependency injection or lazy import
        # For now, we'll try to calculate form directly or reuse existing logic via import if safe
        
        # Let's re-implement the simplified strength logic here to avoid circular imports 
        # with analytics.py/analytics_engine
        
        try:
            from .analytics import get_enhanced_features
            features = get_enhanced_features(home_team, away_team)
            
            home_strength = features.get('home_strength', 0.5)
            away_strength = features.get('away_strength', 0.5)
            
            strength_diff = home_strength - away_strength
            
            # Convert strength difference to probabilities (same logic as before)
            if abs(strength_diff) < 0.03:
                probs = {"Home Team Win": 33.3, "Draw": 33.4, "Away Team Win": 33.3}
            elif strength_diff > 0.20:
                probs = {"Home Team Win": 58.0, "Draw": 24.0, "Away Team Win": 18.0}
            elif strength_diff > 0.12:
                probs = {"Home Team Win": 48.0, "Draw": 30.0, "Away Team Win": 22.0}
            elif strength_diff > 0.08:
                probs = {"Home Team Win": 42.0, "Draw": 32.0, "Away Team Win": 26.0}
            elif strength_diff < -0.20:
                probs = {"Home Team Win": 18.0, "Draw": 24.0, "Away Team Win": 58.0}
            elif strength_diff < -0.12:
                probs = {"Home Team Win": 22.0, "Draw": 30.0, "Away Team Win": 48.0}
            elif strength_diff < -0.08:
                probs = {"Home Team Win": 26.0, "Draw": 32.0, "Away Team Win": 42.0}
            else:
                # Slight advantage to home
                probs = {"Home Team Win": 38.0, "Draw": 32.0, "Away Team Win": 30.0}
            
            logger.info(f"Form-based: {home_team}({home_strength:.2f}) vs "
                   f"{away_team}({away_strength:.2f}) -> Diff:{strength_diff:.2f}")
            
            return probs
        except ImportError:
            # Fallback if circular import
            logger.warning("Could not import get_enhanced_features, using default probabilities")
            return {"Home Team Win": 33.3, "Draw": 33.4, "Away Team Win": 33.3}
        except Exception as e:
            logger.error(f"Error in FormBasedCalculator: {e}")
            return None
    
    def get_strategy_name(self):
        return "Recent Form"


class BlendedCalculator(ProbabilityCalculator):
    """Combines multiple calculators with weights"""
    
    def __init__(self, calculators, weights):
        """
        calculators: list of ProbabilityCalculator instances
        weights: list of floats (must sum to 1.0)
        """
        if len(calculators) != len(weights):
             raise ValueError("Number of calculators must match number of weights")
        # Normalize weights just in case
        total = sum(weights)
        if total > 0:
            self.weights = [w / total for w in weights]
        else:
            self.weights = [1.0 / len(weights)] * len(weights)
            
        self.calculators = calculators
    
    def calculate(self, home_team, away_team, data, adapter):
        results = []
        used_calculators = []
        used_weights = []
        
        # Try each calculator
        for calc, weight in zip(self.calculators, self.weights):
            result = calc.calculate(home_team, away_team, data, adapter)
            if result is not None:
                results.append(result)
                used_calculators.append(calc)
                used_weights.append(weight)
        
        if not results:
            return None
        
        # Renormalize weights if some calculators failed
        total_weight = sum(used_weights)
        if total_weight == 0:
             return {"Home Team Win": 33.3, "Draw": 33.4, "Away Team Win": 33.3}
             
        normalized_weights = [w / total_weight for w in used_weights]
        
        # Blend the results
        blended = {"Home Team Win": 0.0, "Draw": 0.0, "Away Team Win": 0.0}
        for result, weight in zip(results, normalized_weights):
            for key in blended:
                blended[key] += result.get(key, 0) * weight
        
        # Log which strategies were used
        strategy_names = [c.get_strategy_name() for c in used_calculators]
        logger.info(f"Blended Strategy: Used {strategy_names} for {home_team} vs {away_team}")
        
        return blended
    
    def get_strategy_name(self):
        return "Blended"
