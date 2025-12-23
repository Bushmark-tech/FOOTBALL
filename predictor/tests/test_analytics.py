"""
Tests for analytics and prediction logic.
"""
from django.test import TestCase
from predictor.analytics import (
    determine_final_prediction,
    calculate_probabilities_original,
    get_column_names
)
import pandas as pd
import numpy as np


class DetermineFinalPredictionTest(TestCase):
    """Test cases for determine_final_prediction function."""
    
    def test_determine_final_prediction_class_index_away(self):
        """Test with class index 0 (Away - new mapping)."""
        pred = 0
        probs = {
            'Home Team Win': 20.0,
            'Draw': 25.0,
            'Away Team Win': 55.0
        }
        result = determine_final_prediction(pred, probs)
        self.assertEqual(result, 'Away Team Win')
    
    def test_determine_final_prediction_class_index_draw(self):
        """Test with class index 1 (Draw)."""
        pred = 1
        probs = {
            'Home Team Win': 30.0,
            'Draw': 50.0,
            'Away Team Win': 20.0
        }
        result = determine_final_prediction(pred, probs)
        self.assertEqual(result, 'Draw')
    
    def test_determine_final_prediction_class_index_home(self):
        """Test with class index 2 (Home - new mapping)."""
        pred = 2
        probs = {
            'Home Team Win': 60.0,
            'Draw': 25.0,
            'Away Team Win': 15.0
        }
        result = determine_final_prediction(pred, probs)
        self.assertEqual(result, 'Home Team Win')
    
    def test_determine_final_prediction_double_chance_home_draw(self):
        """Test when Home and Draw are tied, but model predicts Away (triggers double chance)."""
        pred = 0  # Model predicts Away (new mapping: 0=Away), but Home and Draw are tied
        probs = {
            'Home Team Win': 40.0,
            'Draw': 40.0,
            'Away Team Win': 20.0
        }
        result = determine_final_prediction(pred, probs)
        # Since model predicts Away but Home and Draw are tied, should return "Home Team Win or Draw"
        self.assertIn('or', result)
        self.assertIn('Home Team Win', result)
        self.assertIn('Draw', result)
    
    def test_determine_final_prediction_double_chance_away_draw(self):
        """Test when Away and Draw are tied, but model predicts Home (triggers double chance)."""
        pred = 2  # Model predicts Home (new mapping: 2=Home), but Away and Draw are tied
        probs = {
            'Home Team Win': 20.0,
            'Draw': 40.0,
            'Away Team Win': 40.0
        }
        result = determine_final_prediction(pred, probs)
        # Since model predicts Home but Away and Draw are tied, should return "Away Team Win or Draw"
        self.assertIn('or', result)
        self.assertIn('Away Team Win', result)
        self.assertIn('Draw', result)
    
    def test_determine_final_prediction_model_prioritized(self):
        """Test that model prediction is prioritized over historical probabilities."""
        pred = 0  # Model predicts Away (new mapping: 0=Away)
        probs = {
            'Home Team Win': 45.0,  # Historical suggests Home
            'Draw': 25.0,
            'Away Team Win': 30.0   # but model predicts Away
        }
        result = determine_final_prediction(pred, probs)
        # Model prediction should be prioritized over historical probabilities
        self.assertEqual(result, 'Away Team Win')
    
    def test_determine_final_prediction_no_probs(self):
        """Test with no historical probabilities."""
        pred = 1
        probs = None
        result = determine_final_prediction(pred, probs)
        self.assertEqual(result, 'Draw')
    
    def test_determine_final_prediction_numeric_range(self):
        """Test with numeric range format (0.5-3.4)."""
        pred = 2.8  # Home range (2.5-3.4 maps to Home in new mapping)
        probs = {
            'Home Team Win': 55.0,
            'Draw': 30.0,
            'Away Team Win': 15.0
        }
        result = determine_final_prediction(pred, probs)
        self.assertEqual(result, 'Home Team Win')


class CalculateProbabilitiesTest(TestCase):
    """Test cases for calculate_probabilities_original function."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample match data
        self.data = pd.DataFrame({
            'HomeTeam': ['Man City', 'Man City', 'Liverpool', 'Liverpool'],
            'AwayTeam': ['Liverpool', 'Chelsea', 'Man City', 'Chelsea'],
            'FTR': ['H', 'D', 'A', 'H'],
            'FTHG': [2, 1, 0, 3],
            'FTAG': [1, 1, 2, 1]
        })
    
    def test_calculate_probabilities_with_data(self):
        """Test calculating probabilities with match data."""
        probs = calculate_probabilities_original(
            'Man City',
            'Liverpool',
            self.data,
            version='v1'
        )
        
        self.assertIsNotNone(probs)
        self.assertIn('Home Team Win', probs)
        self.assertIn('Draw', probs)
        self.assertIn('Away Team Win', probs)
        # Probabilities should sum to approximately 100
        total = sum(probs.values())
        self.assertAlmostEqual(total, 100.0, delta=1.0)
    
    def test_calculate_probabilities_no_data(self):
        """Test calculating probabilities with no match data."""
        empty_data = pd.DataFrame()
        probs = calculate_probabilities_original(
            'Team A',
            'Team B',
            empty_data,
            version='v1'
        )
        
        # Should return fallback probabilities
        self.assertIsNotNone(probs)
        self.assertIn('Home Team Win', probs)


class GetColumnNamesTest(TestCase):
    """Test cases for get_column_names function."""
    
    def test_get_column_names_v1(self):
        """Test getting column names for version 1."""
        home_col, away_col, result_col = get_column_names('v1')
        self.assertEqual(home_col, 'HomeTeam')
        self.assertEqual(away_col, 'AwayTeam')
        self.assertEqual(result_col, 'FTR')
    
    def test_get_column_names_v2(self):
        """Test getting column names for version 2."""
        home_col, away_col, result_col = get_column_names('v2')
        self.assertEqual(home_col, 'Home')
        self.assertEqual(away_col, 'Away')
        self.assertEqual(result_col, 'Res')  # v2 uses 'Res' not 'FTR'

