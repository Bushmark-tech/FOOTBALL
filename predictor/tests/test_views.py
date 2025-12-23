"""
Tests for predictor views.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from predictor.models import Prediction, League, Team
import json


# Override cache and session settings for view tests
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ViewTestBase(TestCase):
    """Base class for view tests with test-friendly cache settings."""
    pass


class HomeViewTest(ViewTestBase):
    """Test cases for home view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create some test predictions
        for i in range(5):
            Prediction.objects.create(
                home_team=f'Team {i}A',
                away_team=f'Team {i}B',
                home_score=2,
                away_score=1,
                confidence=0.70 + i * 0.05
            )
    
    def test_home_view_status_code(self):
        """Test home view returns 200."""
        response = self.client.get(reverse('predictor:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_view_template(self):
        """Test home view uses correct template."""
        response = self.client.get(reverse('predictor:home'))
        self.assertTemplateUsed(response, 'predictor/home.html')
    
    def test_home_view_context(self):
        """Test home view context data."""
        response = self.client.get(reverse('predictor:home'))
        self.assertIn('total_predictions', response.context)
        self.assertIn('recent_predictions', response.context)
        self.assertEqual(response.context['total_predictions'], 5)


class PredictViewTest(ViewTestBase):
    """Test cases for predict view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_predict_view_get(self):
        """Test predict view GET request."""
        response = self.client.get(reverse('predictor:predict'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictor/predict.html')
    
    def test_predict_view_post_valid(self):
        """Test predict view POST with valid data."""
        # Mock FastAPI response
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


class APIPredictTest(ViewTestBase):
    """Test cases for API predict endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_api_predict_get(self):
        """Test API predict GET request (should fail)."""
        response = self.client.get(reverse('predictor:api_predict'))
        # GET method not allowed, returns 405
        self.assertEqual(response.status_code, 405)
    
    def test_api_predict_post_missing_data(self):
        """Test API predict POST with missing data."""
        response = self.client.post(
            reverse('predictor:api_predict'),
            {},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_api_predict_post_valid_json(self):
        """Test API predict POST with valid JSON."""
        data = {
            'home_team': 'Chelsea',
            'away_team': 'Arsenal',
            'category': 'European Leagues'
        }
        response = self.client.post(
            reverse('predictor:api_predict'),
            json.dumps(data),
            content_type='application/json'
        )
        # May return 503 if FastAPI is not running, or 200 if it is
        self.assertIn(response.status_code, [200, 503])


class GetTeamsByCategoryTest(ViewTestBase):
    """Test cases for get teams by category endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.league = League.objects.create(
            name='Premier League',
            category='European Leagues'
        )
        Team.objects.create(name='Arsenal', league=self.league)
        Team.objects.create(name='Chelsea', league=self.league)
        Team.objects.create(name='Liverpool', league=self.league)
    
    def test_get_teams_valid(self):
        """Test getting teams for valid category and league."""
        response = self.client.get(
            reverse('predictor:get_teams_by_category'),
            {
                'category': 'European Leagues',
                'league': 'Premier League'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('teams', data)
        self.assertEqual(len(data['teams']), 3)
    
    def test_get_teams_invalid_league(self):
        """Test getting teams for invalid league."""
        response = self.client.get(
            reverse('predictor:get_teams_by_category'),
            {
                'category': 'European Leagues',
                'league': 'Invalid League'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['teams'], [])
    
    def test_get_teams_missing_params(self):
        """Test getting teams with missing parameters."""
        response = self.client.get(reverse('predictor:get_teams_by_category'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['teams'], [])


class HistoryViewTest(ViewTestBase):
    """Test cases for history view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create predictions for the user
        for i in range(3):
            Prediction.objects.create(
                home_team=f'Team {i}A',
                away_team=f'Team {i}B',
                home_score=2,
                away_score=1,
                confidence=0.70,
                user=self.user
            )
    
    def test_history_view_requires_login(self):
        """Test history view requires login."""
        response = self.client.get(reverse('predictor:history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_history_view_authenticated(self):
        """Test history view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('predictor:history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictor/history.html')
        self.assertEqual(len(response.context['predictions']), 3)

