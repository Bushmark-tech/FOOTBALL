from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Predictor(ABC):
    """Base class for all predictors"""
    
    @abstractmethod
    def preprocess(self, home_team, away_team, data, adapter):
        """Prepare features for model"""
        pass
    
    @abstractmethod
    def predict(self, features):
        """Get prediction and probabilities"""
        pass
    
    @abstractmethod
    def get_model_type(self):
        pass

class Model1Predictor(Predictor):
    """For European leagues - uses one-hot encoding"""
    
    def __init__(self, model):
        self.model = model
    
    def preprocess(self, home_team, away_team, data, adapter):
        # Delegate to the function in analytics.py (to keep logic centralized and avoid circular deps if possible)
        # However, cleaner design is to move logic here.
        # For now, we utilize the existing `preprocess_for_models` 
        # but we must be careful imports.
        # Actually, `preprocess_for_models` is designed to handle both models.
        # We can just call it.
        try:
             from .analytics import preprocess_for_models
             return preprocess_for_models(home_team, away_team, self.model, data)
        except ImportError:
             logger.error("Could not import preprocess_for_models")
             return None
    
    def predict(self, features):
        if features is None:
             return None, None
             
        try:
            pred = self.model.predict(features)[0]
            
            # Helper to safely get probabilities
            if hasattr(self.model, 'predict_proba'):
                 probs = self.model.predict_proba(features)[0]
                 # Convert to standard format 0, 1, 2
                 # Assuming classes are ordered 0(Away), 1(Draw), 2(Home) or similar
                 # We need to rely on model classes
                 if hasattr(self.model, 'classes_'):
                      # Basic mapping logic (simplified from analytics.py giant block)
                      prob_dict = {}
                      for i, cls in enumerate(self.model.classes_):
                           cls_str = str(cls).upper()
                           if cls_str in ['0', 'A', 'AWAY']: prob_dict[0] = probs[i]
                           elif cls_str in ['1', 'D', 'DRAW']: prob_dict[1] = probs[i]
                           elif cls_str in ['2', 'H', 'HOME']: prob_dict[2] = probs[i]
                           else:
                                # Fallback based on index
                                prob_dict[i] = probs[i]
                 else:
                      prob_dict = {0: probs[0], 1: probs[1], 2: probs[2]}
            else:
                 prob_dict = {0: 0.33, 1: 0.34, 2: 0.33}
                 
            return pred, prob_dict
        except Exception as e:
             logger.error(f"Prediction error in Model1: {e}")
             return None, None
    
    def get_model_type(self):
        return "Model1"


class Model2Predictor(Predictor):
    """For other leagues - uses team IDs"""
    
    def __init__(self, model, team_mapping):
        self.model = model
        self.team_mapping = team_mapping
    
    def preprocess(self, home_team, away_team, data, adapter):
        # Calls the same preprocessing function which detects model features
        try:
             from .analytics import preprocess_for_models
             return preprocess_for_models(home_team, away_team, self.model, data)
        except ImportError:
             logger.error("Could not import preprocess_for_models")
             return None
    
    def predict(self, features):
        if features is None:
             return None, None
             
        try:
            # Check if classifier or regressor
            if hasattr(self.model, 'predict_proba'):
                pred = self.model.predict(features)[0]
                probs = self.model.predict_proba(features)[0]
                # Default mapping
                prob_dict = {0: probs[0], 1: probs[1], 2: probs[2]}
                return pred, prob_dict
            else:
                # Regressor - predict total goals or similar?
                # The user's prompt suggested converting total goals to outcome, but existing code 
                # returns just a prediction number for regressors usually?
                # Actually existing code handles regressors by checking `is_regressor`.
                # We'll stick to basic prediction here.
                pred = self.model.predict(features)[0]
                return pred, {} 
        except Exception as e:
             logger.error(f"Prediction error in Model2: {e}")
             return None, None
    
    def get_model_type(self):
        return "Model2"

class ModelFactory:
    """Creates the right predictor based on teams"""
    
    def __init__(self, team_categories):
        # team_categories is dict with 'main_teams', 'other_teams' sets/lists
        self.team_categories = team_categories
    
    def create_predictor(self, home_team, away_team, model1, model2, team_mapping, category=None):
        """
        Factory method - returns the appropriate predictor
        
        Args:
            category: League category ('European Leagues' or 'Others')
        """
        # Priority 1: Use category if provided (Strict Enforcement)
        if category:
            if category == 'European Leagues':
                logger.info(f"Using Model1 for European League match: {home_team} vs {away_team}")
                return Model1Predictor(model1)
            elif category == 'Others':
                logger.info(f"Using Model2 for Others match: {home_team} vs {away_team}")
                return Model2Predictor(model2, team_mapping)
            else:
                # Fallback for unknown category -> check teams
                logger.info(f"Unknown category '{category}', checking teams for model selection")

        # Priority 2: Check team categories (if category missing or unknown)
        main_teams = self.team_categories.get('main_teams', [])
        other_teams = self.team_categories.get('other_teams', [])
        
        # If both are in main (European)
        if home_team in main_teams and away_team in main_teams:
            logger.info(f"Using Model1 for main teams: {home_team} vs {away_team}")
            return Model1Predictor(model1)
        
        # If both are in other
        elif home_team in other_teams and away_team in other_teams:
            logger.info(f"Using Model2 for other teams: {home_team} vs {away_team}")
            return Model2Predictor(model2, team_mapping)
            
        else:
            # Fallback Logic:
            # If teams are mixed or unknown, we default to Model2 as it's more flexible with string names.
            # Ideally, this should trigger Form-based fallback if Model2 also fails.
            logger.info(f"Mixed or unknown teams: {home_team} vs {away_team}, defaulting to Model2")
            return Model2Predictor(model2, team_mapping)
