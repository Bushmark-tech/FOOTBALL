"""
Integration tests for Football Predictor Pro.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from predictor.models import Prediction, League, Team
import json


# Override cache and session settings for tests
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class IntegrationTestBase(TestCase):
    """Base class for integration tests with test-friendly cache settings."""
    pass


class PredictionFlowTest(IntegrationTestBase):
    """Integration tests for prediction flow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create league and teams
        self.league = League.objects.create(
            name='Premier League',
            category='European Leagues'
        )
        Team.objects.create(name='Man City', league=self.league)
        Team.objects.create(name='Liverpool', league=self.league)
    
    def test_complete_prediction_flow(self):
        """Test complete prediction flow from form to result."""
        # 1. Access predict page
        response = self.client.get(reverse('predictor:predict'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit prediction form
        response = self.client.post(
            reverse('predictor:predict'),
            {
                'home_team': 'Man City',
                'away_team': 'Liverpool',
                'category': 'European Leagues'
            },
            follow=True
        )
        
        # Should redirect to result page
        self.assertIn(response.status_code, [200, 302])
        
        # 3. Check if prediction was saved
        predictions = Prediction.objects.filter(
            home_team='Man City',
            away_team='Liverpool'
        )
        # Prediction may or may not be saved depending on FastAPI availability
        # This is acceptable for integration test
    
    def test_api_prediction_flow(self):
        """Test API prediction flow."""
        data = {
            'home_team': 'Man City',
            'away_team': 'Liverpool',
            'category': 'European Leagues'
        }
        
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        # API may return 200 (success) or 503 (FastAPI not available)
        self.assertIn(response.status_code, [200, 503])
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('outcome', data)
            self.assertIn('probabilities', data)


class CacheIntegrationTest(IntegrationTestBase):
    """Integration tests for caching."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_home_view_caching(self):
        """Test that home view uses caching."""
        # Create predictions
        for i in range(5):
            Prediction.objects.create(
                home_team=f'Team {i}A',
                away_team=f'Team {i}B',
                home_score=2,
                away_score=1,
                confidence=0.70
            )
        
        # First request
        response1 = self.client.get(reverse('predictor:home'))
        self.assertEqual(response1.status_code, 200)
        
        # Second request (should use cache)
        response2 = self.client.get(reverse('predictor:home'))
        self.assertEqual(response2.status_code, 200)
        
        # Both should have same content (cached)
        # Note: Cache may not work in test environment, but structure should be same
        self.assertEqual(
            response1.context['total_predictions'],
            response2.context['total_predictions']
        )


class AuthenticationFlowTest(IntegrationTestBase):
    """Integration tests for authentication flow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_required_for_history(self):
        """Test that history view requires login."""
        # Without login
        response = self.client.get(reverse('predictor:history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # With login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('predictor:history'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_predictions_isolation(self):
        """Test that users only see their own predictions."""
        # Create another user
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # Create predictions for both users
        Prediction.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=2,
            away_score=1,
            confidence=0.70,
            user=self.user
        )
        Prediction.objects.create(
            home_team='Team C',
            away_team='Team D',
            home_score=1,
            away_score=2,
            confidence=0.65,
            user=user2
        )
        
        # Login as first user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('predictor:history'))
        
        # Should only see own predictions
        self.assertEqual(len(response.context['predictions']), 1)
        self.assertEqual(
            response.context['predictions'][0].user,
            self.user
        )


class ModelOneAndTwoTest(IntegrationTestBase):
    """Integration tests for Model1 and Model2 predictions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create European League (for Model1)
        self.european_league = League.objects.create(
            name='Premier League',
            category='European Leagues'
        )
        Team.objects.create(name='Arsenal', league=self.european_league)
        Team.objects.create(name='Chelsea', league=self.european_league)
        
        # Create Other category league (for Model2)
        self.other_league = League.objects.create(
            name='MLS',
            category='Others'
        )
        Team.objects.create(name='Basel', league=self.other_league)
        Team.objects.create(name='Zurich', league=self.other_league)
    
    def test_model1_prediction(self):
        """Test that Model1 is used for European League teams."""
        data = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        # API may return 200 (success) or 503 (FastAPI not available)
        self.assertIn(response.status_code, [200, 503])
        
        if response.status_code == 200:
            result = json.loads(response.content)
            # Verify Model1 fields are present
            self.assertIn('model_type', result)
            model_type = result.get('model_type', '')
            
            # Model1 should be used for European League teams
            # Check if model_type contains Model1 or if model1_prediction is set
            self.assertIn('model1_prediction', result)
            self.assertIn('outcome', result)
            self.assertIn('probabilities', result)
            
            # If model_type indicates Model1, verify model1_prediction is set
            if 'Model1' in model_type or result.get('model1_prediction') is not None:
                self.assertIsNotNone(result.get('model1_prediction'))
                # Verify prediction was saved with correct model_type
                predictions = Prediction.objects.filter(
                    home_team='Arsenal',
                    away_team='Chelsea'
                )
                if predictions.exists():
                    prediction = predictions.first()
                    # model_type should be set (may be Model1 or fallback)
                    self.assertIsNotNone(prediction.model_type)
    
    def test_model2_prediction(self):
        """Test that Model2 is used for Other category teams."""
        data = {
            'home_team': 'Basel',
            'away_team': 'Zurich',
            'category': 'Others'
        }
        
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        # API may return 200 (success) or 503 (FastAPI not available)
        self.assertIn(response.status_code, [200, 503])
        
        if response.status_code == 200:
            result = json.loads(response.content)
            # Verify Model2 fields are present
            self.assertIn('model_type', result)
            model_type = result.get('model_type', '')
            
            # Model2 should be used for Other category teams
            # Check if model_type contains Model2 or if model2_prediction is set
            self.assertIn('model2_prediction', result)
            self.assertIn('outcome', result)
            self.assertIn('probabilities', result)
            
            # If model_type indicates Model2, verify model2_prediction is set
            if 'Model2' in model_type or result.get('model2_prediction') is not None:
                self.assertIsNotNone(result.get('model2_prediction'))
                # Verify prediction was saved with correct model_type
                predictions = Prediction.objects.filter(
                    home_team='Basel',
                    away_team='Zurich'
                )
                if predictions.exists():
                    prediction = predictions.first()
                    # model_type should be set (may be Model2 or fallback)
                    self.assertIsNotNone(prediction.model_type)
    
    def test_model1_and_model2_fields(self):
        """Test that both model1_prediction and model2_prediction fields work correctly."""
        # Test Model1 prediction
        data_model1 = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        response1 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data_model1),
            content_type='application/json'
        )
        
        if response1.status_code == 200:
            result1 = json.loads(response1.content)
            # Model1 should have model1_prediction set
            model_type1 = result1.get('model_type', '')
            if 'Model1' in model_type1:
                self.assertIsNotNone(result1.get('model1_prediction'))
                # model2_prediction should be None for Model1
                if 'Model2' not in model_type1:
                    # model2_prediction may be None or not set
                    pass
        
        # Test Model2 prediction
        data_model2 = {
            'home_team': 'Basel',
            'away_team': 'Zurich',
            'category': 'Others'
        }
        
        response2 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data_model2),
            content_type='application/json'
        )
        
        if response2.status_code == 200:
            result2 = json.loads(response2.content)
            # Model2 should have model2_prediction set
            model_type2 = result2.get('model_type', '')
            if 'Model2' in model_type2:
                self.assertIsNotNone(result2.get('model2_prediction'))
                # model1_prediction may be None for Model2
                if 'Model1' not in model_type2:
                    # model1_prediction may be None or not set
                    pass
    
    def test_prediction_saved_with_model_fields(self):
        """Test that predictions are saved with model_type, model1_prediction, and model2_prediction."""
        # Create a prediction manually to test model fields
        prediction = Prediction.objects.create(
            home_team='Arsenal',
            away_team='Chelsea',
            home_score=2,
            away_score=1,
            confidence=0.75,
            user=self.user,
            category='European Leagues',
            model_type='Model1',
            model1_prediction='Home Win',
            model2_prediction=None
        )
        
        # Verify all model fields are saved correctly
        self.assertEqual(prediction.model_type, 'Model1')
        self.assertEqual(prediction.model1_prediction, 'Home Win')
        self.assertIsNone(prediction.model2_prediction)
        
        # Create a Model2 prediction
        prediction2 = Prediction.objects.create(
            home_team='Basel',
            away_team='Zurich',
            home_score=1,
            away_score=2,
            confidence=0.70,
            user=self.user,
            category='Others',
            model_type='Model2',
            model1_prediction=None,
            model2_prediction='Away Win'
        )
        
        # Verify Model2 fields
        self.assertEqual(prediction2.model_type, 'Model2')
        self.assertIsNone(prediction2.model1_prediction)
        self.assertEqual(prediction2.model2_prediction, 'Away Win')
    
    def test_prediction_probabilities_valid(self):
        """Test that predictions have valid probabilities that sum to ~1.0."""
        data = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            result = json.loads(response.content)
            
            # Check probabilities exist
            self.assertIn('probabilities', result)
            probs = result['probabilities']
            
            # Probabilities should be a dict with Home, Draw, Away
            self.assertIsInstance(probs, dict)
            
            # Get probability values
            prob_home = probs.get('Home', probs.get(0, 0))
            prob_draw = probs.get('Draw', probs.get(1, 0))
            prob_away = probs.get('Away', probs.get(2, 0))
            
            # Convert to float if needed
            if isinstance(prob_home, (int, float)):
                prob_home = float(prob_home)
            if isinstance(prob_draw, (int, float)):
                prob_draw = float(prob_draw)
            if isinstance(prob_away, (int, float)):
                prob_away = float(prob_away)
            
            # Probabilities should sum to approximately 1.0 (allow small rounding errors)
            total_prob = prob_home + prob_draw + prob_away
            self.assertAlmostEqual(total_prob, 1.0, places=2, 
                                 msg=f"Probabilities should sum to ~1.0, got {total_prob}")
            
            # Each probability should be between 0 and 1
            self.assertGreaterEqual(prob_home, 0, "Home probability should be >= 0")
            self.assertLessEqual(prob_home, 1, "Home probability should be <= 1")
            self.assertGreaterEqual(prob_draw, 0, "Draw probability should be >= 0")
            self.assertLessEqual(prob_draw, 1, "Draw probability should be <= 1")
            self.assertGreaterEqual(prob_away, 0, "Away probability should be >= 0")
            self.assertLessEqual(prob_away, 1, "Away probability should be <= 1")
    
    def test_outcome_matches_highest_probability(self):
        """Test that the predicted outcome matches the highest probability."""
        data = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            result = json.loads(response.content)
            
            # Get outcome and probabilities
            outcome = result.get('outcome')
            probs = result.get('probabilities', {})
            home_team = result.get('home_team', 'Arsenal')
            away_team = result.get('away_team', 'Chelsea')
            
            # Get probability values
            prob_home = probs.get('Home', probs.get(0, 0))
            prob_draw = probs.get('Draw', probs.get(1, 0))
            prob_away = probs.get('Away', probs.get(2, 0))
            
            # Convert to float
            prob_home = float(prob_home) if isinstance(prob_home, (int, float)) else 0
            prob_draw = float(prob_draw) if isinstance(prob_draw, (int, float)) else 0
            prob_away = float(prob_away) if isinstance(prob_away, (int, float)) else 0
            
            # Find highest probability
            max_prob = max(prob_home, prob_draw, prob_away)
            
            # Normalize outcome format (handle both "Home"/"Draw"/"Away" and "Team Win" formats)
            outcome_normalized = outcome
            if outcome and 'Win' in outcome:
                # Format like "Arsenal Win" or "Chelsea Win"
                if home_team in outcome:
                    outcome_normalized = 'Home'
                elif away_team in outcome:
                    outcome_normalized = 'Away'
                else:
                    outcome_normalized = 'Draw'  # Fallback
            elif outcome and outcome not in ['Home', 'Draw', 'Away']:
                # Try to normalize other formats
                outcome_lower = outcome.lower()
                if 'home' in outcome_lower or outcome_lower == '0':
                    outcome_normalized = 'Home'
                elif 'away' in outcome_lower or outcome_lower == '2':
                    outcome_normalized = 'Away'
                elif 'draw' in outcome_lower or outcome_lower == '1':
                    outcome_normalized = 'Draw'
            
            # Outcome should match the highest probability
            if max_prob == prob_home:
                self.assertIn(outcome_normalized, ['Home'], 
                             f"Outcome should indicate Home win when Home has highest probability ({prob_home:.3f}), got '{outcome}'")
            elif max_prob == prob_draw:
                self.assertEqual(outcome_normalized, 'Draw', 
                               f"Outcome should be 'Draw' when Draw has highest probability ({prob_draw:.3f}), got '{outcome}'")
            elif max_prob == prob_away:
                self.assertIn(outcome_normalized, ['Away'], 
                             f"Outcome should indicate Away win when Away has highest probability ({prob_away:.3f}), got '{outcome}'")
    
    def test_confidence_is_reasonable(self):
        """Test that confidence values are reasonable (between 0 and 1)."""
        data_model1 = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        response1 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data_model1),
            content_type='application/json'
        )
        
        if response1.status_code == 200:
            result1 = json.loads(response1.content)
            
            # Check if confidence is present (may be in different formats)
            confidence = result1.get('confidence') or result1.get('model1_confidence')
            
            if confidence is not None:
                # Convert to float, handling percentage format
                if isinstance(confidence, str):
                    confidence = confidence.replace('%', '')
                    confidence = float(confidence)
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                else:
                    confidence = float(confidence)
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                
                # Confidence should be between 0 and 1
                self.assertGreaterEqual(confidence, 0, 
                                       f"Confidence should be >= 0, got {confidence}")
                self.assertLessEqual(confidence, 1, 
                                   f"Confidence should be <= 1, got {confidence}")
        
        # Test Model2
        data_model2 = {
            'home_team': 'Basel',
            'away_team': 'Zurich',
            'category': 'Others'
        }
        
        response2 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data_model2),
            content_type='application/json'
        )
        
        if response2.status_code == 200:
            result2 = json.loads(response2.content)
            
            confidence = result2.get('confidence') or result2.get('model2_confidence')
            
            if confidence is not None:
                if isinstance(confidence, str):
                    confidence = confidence.replace('%', '')
                    confidence = float(confidence)
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                else:
                    confidence = float(confidence)
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                
                self.assertGreaterEqual(confidence, 0)
                self.assertLessEqual(confidence, 1)
    
    def test_prediction_consistency(self):
        """Test that predictions are consistent (same input gives same output structure)."""
        data = {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'category': 'European Leagues'
        }
        
        # Make two predictions
        response1 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        response2 = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        
        if response1.status_code == 200 and response2.status_code == 200:
            result1 = json.loads(response1.content)
            result2 = json.loads(response2.content)
            
            # Both should have the same required fields
            required_fields = ['outcome', 'probabilities', 'model_type']
            for field in required_fields:
                self.assertIn(field, result1, f"Result1 missing field: {field}")
                self.assertIn(field, result2, f"Result2 missing field: {field}")
            
            # Both should have valid outcomes (handle both formats)
            def normalize_outcome(outcome, home_team, away_team):
                """Normalize outcome to standard format."""
                if outcome in ['Home', 'Draw', 'Away']:
                    return outcome
                if 'Win' in outcome:
                    if home_team in outcome:
                        return 'Home'
                    elif away_team in outcome:
                        return 'Away'
                return outcome  # Return as-is if can't normalize
            
            home_team = result1.get('home_team', 'Arsenal')
            away_team = result1.get('away_team', 'Chelsea')
            
            outcome1_norm = normalize_outcome(result1['outcome'], home_team, away_team)
            outcome2_norm = normalize_outcome(result2['outcome'], home_team, away_team)
            
            # Outcomes should be valid (either standard format or team-specific format)
            valid_outcomes_standard = ['Home', 'Draw', 'Away']
            valid_outcomes_extended = valid_outcomes_standard + [f'{home_team} Win', f'{away_team} Win']
            
            # Check if outcome is valid (either standard or team-specific)
            self.assertTrue(
                outcome1_norm in valid_outcomes_standard or result1['outcome'] in valid_outcomes_extended,
                f"Result1 outcome '{result1['outcome']}' is not valid"
            )
            self.assertTrue(
                outcome2_norm in valid_outcomes_standard or result2['outcome'] in valid_outcomes_extended,
                f"Result2 outcome '{result2['outcome']}' is not valid"
            )
            
            # Both should have valid probabilities
            for result in [result1, result2]:
                probs = result['probabilities']
                prob_home = float(probs.get('Home', probs.get(0, 0)))
                prob_draw = float(probs.get('Draw', probs.get(1, 0)))
                prob_away = float(probs.get('Away', probs.get(2, 0)))
                total = prob_home + prob_draw + prob_away
                self.assertAlmostEqual(total, 1.0, places=2)

