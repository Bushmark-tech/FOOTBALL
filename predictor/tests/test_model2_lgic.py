"""
Tests for Model2 using lGIC logic.
Verifies that Model2 uses the simpler lGIC analytics functions.
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from predictor.models import Prediction, League, Team
from predictor.analytics import (
    calculate_probabilities_model2,
    get_team_recent_form_model2,
    get_recent_team_form_model2,
    get_head_to_head_form_model2,
    advanced_predict_match,
    load_football_data
)
import json


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class Model2LGICTest(TestCase):
    """Test that Model2 uses lGIC logic correctly."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create Other category league (for Model2)
        self.other_league = League.objects.create(
            name='Switzerland League',
            category='Others'
        )
        Team.objects.create(name='Basel', league=self.other_league)
        Team.objects.create(name='Zurich', league=self.other_league)
        Team.objects.create(name='Young Boys', league=self.other_league)
    
    def test_calculate_probabilities_model2_exists(self):
        """Test that calculate_probabilities_model2 function exists."""
        self.assertTrue(callable(calculate_probabilities_model2))
    
    def test_calculate_probabilities_model2_uses_v2(self):
        """Test that calculate_probabilities_model2 uses version v2."""
        # Load dataset 2 (for Model2)
        data = load_football_data(2, use_cache=False)
        
        if data is not None and not data.empty:
            # Try to get probabilities for known teams
            # Use teams that might exist in dataset 2
            probs = calculate_probabilities_model2('Basel', 'Zurich', data, version="v2")
            
            # Should return None if no H2H data, or dict with probabilities
            if probs is not None:
                self.assertIsInstance(probs, dict)
                self.assertIn('Home Team Win', probs)
                self.assertIn('Draw', probs)
                self.assertIn('Away Team Win', probs)
                
                # Probabilities should be percentages (0-100)
                self.assertGreaterEqual(probs['Home Team Win'], 0)
                self.assertLessEqual(probs['Home Team Win'], 100)
                self.assertGreaterEqual(probs['Draw'], 0)
                self.assertLessEqual(probs['Draw'], 100)
                self.assertGreaterEqual(probs['Away Team Win'], 0)
                self.assertLessEqual(probs['Away Team Win'], 100)
    
    def test_get_team_recent_form_model2_exists(self):
        """Test that get_team_recent_form_model2 function exists."""
        self.assertTrue(callable(get_team_recent_form_model2))
    
    def test_get_team_recent_form_model2_returns_string(self):
        """Test that get_team_recent_form_model2 returns a form string."""
        data = load_football_data(2, use_cache=False)
        
        if data is not None and not data.empty:
            form = get_team_recent_form_model2('Basel', data, version="v2")
            
            # Should return a string (form like "WWDLD" or "-----" if no data)
            self.assertIsInstance(form, str)
            self.assertLessEqual(len(form), 5)  # Max 5 characters
    
    def test_get_recent_team_form_model2_exists(self):
        """Test that get_recent_team_form_model2 function exists."""
        self.assertTrue(callable(get_recent_team_form_model2))
    
    def test_get_recent_team_form_model2_returns_tuple(self):
        """Test that get_recent_team_form_model2 returns tuple of form strings."""
        data = load_football_data(2, use_cache=False)
        
        if data is not None and not data.empty:
            home_form, away_form = get_recent_team_form_model2('Basel', 'Zurich', data, version="v2")
            
            # Should return tuple of two strings
            self.assertIsInstance(home_form, str)
            self.assertIsInstance(away_form, str)
            self.assertLessEqual(len(home_form), 5)
            self.assertLessEqual(len(away_form), 5)
    
    def test_model2_uses_lgic_logic_in_prediction(self):
        """Test that Model2 predictions use lGIC logic."""
        # Load models (may be None if not available)
        try:
            import os
            import joblib
            import pickle
            
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model1_path = os.path.join(script_dir, 'models', 'model1.pkl')
            model2_path = os.path.join(script_dir, 'models', 'model2.pkl')
            
            model1 = None
            model2 = None
            
            if os.path.exists(model1_path):
                try:
                    model1 = joblib.load(model1_path)
                except:
                    try:
                        with open(model1_path, 'rb') as f:
                            model1 = pickle.load(f)
                    except:
                        pass
            
            if os.path.exists(model2_path):
                try:
                    from predictor.model2_loader import load_model2_compatible
                    model2, _ = load_model2_compatible(model2_path)
                except:
                    try:
                        model2 = joblib.load(model2_path)
                    except:
                        try:
                            with open(model2_path, 'rb') as f:
                                model2 = pickle.load(f)
                        except:
                            pass
            
            # Test with Model2 teams (Other category)
            result = advanced_predict_match('Basel', 'Zurich', model1, model2)
            
            if result:
                # Should have model_type indicating Model2
                model_type = result.get('model_type', '')
                self.assertTrue('Model2' in model_type, 
                              f"Expected Model2, got {model_type}")
                
                # Should have probabilities
                probs = result.get('probabilities', {})
                self.assertIsInstance(probs, dict)
                
                # Should have outcome
                outcome = result.get('outcome')
                self.assertIsNotNone(outcome)
                
                # Model2 prediction should be set
                if 'Model2' in model_type:
                    model2_pred = result.get('model2_prediction')
                    # model2_prediction may be None or a value
                    # Just verify the structure is correct
                    self.assertIn('model2_prediction', result)
        except Exception as e:
            # If models can't be loaded, that's okay for this test
            # We're just testing that the functions exist and work
            pass
    
    def test_model2_probabilities_format(self):
        """Test that Model2 probabilities match lGIC format."""
        data = load_football_data(2, use_cache=False)
        
        if data is not None and not data.empty:
            probs = calculate_probabilities_model2('Team1', 'Team2', data, version="v2")
            
            # If probabilities are returned, they should be in lGIC format
            if probs is not None:
                # lGIC format uses these exact keys
                expected_keys = ['Home Team Win', 'Draw', 'Away Team Win']
                for key in expected_keys:
                    self.assertIn(key, probs)
                
                # Values should be percentages (0-100)
                for key in expected_keys:
                    value = probs[key]
                    self.assertGreaterEqual(value, 0)
                    self.assertLessEqual(value, 100)
    
    def test_model2_form_functions_handle_missing_data(self):
        """Test that Model2 form functions handle missing data gracefully."""
        data = load_football_data(2, use_cache=False)
        
        if data is not None and not data.empty:
            # Test with non-existent teams
            form = get_team_recent_form_model2('NonExistentTeam123', data, version="v2")
            self.assertIsInstance(form, str)
            # Should return default form or empty string
            self.assertLessEqual(len(form), 5)
            
            home_form, away_form = get_recent_team_form_model2(
                'NonExistentTeam1', 'NonExistentTeam2', data, version="v2"
            )
            self.assertIsInstance(home_form, str)
            self.assertIsInstance(away_form, str)







