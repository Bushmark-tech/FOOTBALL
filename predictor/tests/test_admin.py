"""
Unit tests for Django Admin functionality
Tests all admin models, actions, and custom displays
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from predictor.models import (
    Prediction, Team, Match, League, BillingUsage, 
    UserProfile, Subscription
)


class AdminAccessTest(TestCase):
    """Test admin panel access and authentication"""
    
    def setUp(self):
        """Set up test client and admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
    
    def test_admin_login(self):
        """Test admin can login"""
        response = self.client.post(reverse('admin:login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_admin_index_access(self):
        """Test admin index page is accessible"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LEON GAMES PRO')
    
    def test_non_admin_cannot_access(self):
        """Test regular users cannot access admin"""
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@gmail.com',
            password='pass123'
        )
        self.client.login(username='regular', password='pass123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class PredictionAdminTest(TestCase):
    """Test Prediction admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test user and prediction
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='pass123'
        )
        self.prediction = Prediction.objects.create(
            home_team='Arsenal',
            away_team='Chelsea',
            home_score=2,
            away_score=1,
            confidence=85.5,
            user=self.user,
            league='Premier League',
            outcome='Home'
        )
    
    def test_prediction_list_view(self):
        """Test prediction list is accessible"""
        url = reverse('admin:predictor_prediction_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arsenal')
        self.assertContains(response, 'Chelsea')
    
    def test_prediction_detail_view(self):
        """Test prediction detail view"""
        url = reverse('admin:predictor_prediction_change', args=[self.prediction.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arsenal')
    
    def test_archive_prediction_action(self):
        """Test archive prediction admin action"""
        url = reverse('admin:predictor_prediction_changelist')
        data = {
            'action': 'archive_predictions',
            '_selected_action': [self.prediction.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify prediction was archived
        self.prediction.refresh_from_db()
        self.assertTrue(self.prediction.is_archived)
        self.assertIsNotNone(self.prediction.archived_date)
    
    def test_unarchive_prediction_action(self):
        """Test unarchive prediction admin action"""
        # First archive it
        self.prediction.is_archived = True
        self.prediction.archived_date = timezone.now()
        self.prediction.save()
        
        url = reverse('admin:predictor_prediction_changelist')
        data = {
            'action': 'unarchive_predictions',
            '_selected_action': [self.prediction.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify prediction was unarchived
        self.prediction.refresh_from_db()
        self.assertFalse(self.prediction.is_archived)


class UserProfileAdminTest(TestCase):
    """Test UserProfile admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test user with profile
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='pass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            free_matches_limit=1,
            free_matches_used=0,
            email_verified=False
        )
    
    def test_userprofile_list_view(self):
        """Test user profile list is accessible"""
        url = reverse('admin:predictor_userprofile_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_verify_user_action(self):
        """Test verify user admin action"""
        url = reverse('admin:predictor_userprofile_changelist')
        data = {
            'action': 'verify_users',
            '_selected_action': [self.profile.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was verified
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.email_verified)
        self.assertIsNone(self.profile.verification_token)
    
    def test_reset_free_quota_action(self):
        """Test reset free quota admin action"""
        # Set some used matches
        self.profile.free_matches_used = 1
        self.profile.save()
        
        url = reverse('admin:predictor_userprofile_changelist')
        data = {
            'action': 'reset_free_quota',
            '_selected_action': [self.profile.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify quota was reset
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.free_matches_used, 0)
    
    def test_email_verified_display(self):
        """Test email verified display shows correct status"""
        url = reverse('admin:predictor_userprofile_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'Not Verified')
        
        # Verify user
        self.profile.email_verified = True
        self.profile.save()
        
        response = self.client.get(url)
        self.assertContains(response, 'Verified')


class SubscriptionAdminTest(TestCase):
    """Test Subscription admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create test user and subscription
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='pass123'
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            status='pending',
            payment_method='mpesa',
            plan_type='standard',
            amount=200.00,
            currency='KSH'
        )
    
    def test_subscription_list_view(self):
        """Test subscription list is accessible"""
        url = reverse('admin:predictor_subscription_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_activate_subscription_action(self):
        """Test activate subscription admin action"""
        url = reverse('admin:predictor_subscription_changelist')
        data = {
            'action': 'activate_subscriptions',
            '_selected_action': [self.subscription.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription was activated
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'active')
    
    def test_cancel_subscription_action(self):
        """Test cancel subscription admin action"""
        url = reverse('admin:predictor_subscription_changelist')
        data = {
            'action': 'cancel_subscriptions',
            '_selected_action': [self.subscription.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription was cancelled
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'cancelled')
    
    def test_extend_subscription_action(self):
        """Test extend subscription admin action"""
        # Set end date
        self.subscription.end_date = timezone.now().date() + timedelta(days=5)
        self.subscription.save()
        original_end_date = self.subscription.end_date
        
        url = reverse('admin:predictor_subscription_changelist')
        data = {
            'action': 'extend_subscriptions',
            '_selected_action': [self.subscription.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify subscription was extended
        self.subscription.refresh_from_db()
        self.assertEqual(
            self.subscription.end_date,
            original_end_date + timedelta(days=30)
        )
    
    def test_plan_type_display(self):
        """Test plan type is displayed correctly"""
        url = reverse('admin:predictor_subscription_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'Standard Plan')


class TeamAdminTest(TestCase):
    """Test Team admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create league and team
        self.league = League.objects.create(
            name='Premier League',
            category='European Leagues',
            country='England'
        )
        self.team = Team.objects.create(
            name='Arsenal',
            league=self.league,
            country='England'
        )
    
    def test_team_list_view(self):
        """Test team list is accessible"""
        url = reverse('admin:predictor_team_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arsenal')
    
    def test_team_detail_view(self):
        """Test team detail view"""
        url = reverse('admin:predictor_team_change', args=[self.team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arsenal')


class LeagueAdminTest(TestCase):
    """Test League admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        self.league = League.objects.create(
            name='Premier League',
            category='European Leagues',
            country='England'
        )
    
    def test_league_list_view(self):
        """Test league list is accessible"""
        url = reverse('admin:predictor_league_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premier League')


class BillingUsageAdminTest(TestCase):
    """Test BillingUsage admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Create user and billing usage
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='pass123'
        )
        self.billing = BillingUsage.objects.create(
            user=self.user,
            total_predictions=5,
            unique_teams_count=4,
            unique_leagues_count=2,
            is_active=True
        )
    
    def test_billing_list_view(self):
        """Test billing usage list is accessible"""
        url = reverse('admin:predictor_billingusage_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_mark_inactive_action(self):
        """Test mark inactive admin action"""
        url = reverse('admin:predictor_billingusage_changelist')
        data = {
            'action': 'mark_inactive',
            '_selected_action': [self.billing.id]
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify billing was marked inactive
        self.billing.refresh_from_db()
        self.assertFalse(self.billing.is_active)
        self.assertIsNotNone(self.billing.session_end)


class MatchAdminTest(TestCase):
    """Test Match admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        self.match = Match.objects.create(
            home_team='Arsenal',
            away_team='Chelsea',
            home_score=2,
            away_score=1,
            match_date=timezone.now().date(),
            league='Premier League',
            season='2023/24'
        )
    
    def test_match_list_view(self):
        """Test match list is accessible"""
        url = reverse('admin:predictor_match_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arsenal')


class AdminCustomizationTest(TestCase):
    """Test admin site customization"""
    
    def setUp(self):
        """Set up test client and admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
    
    def test_admin_site_header(self):
        """Test custom admin site header"""
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'LEON GAMES PRO Admin')
    
    def test_admin_site_title(self):
        """Test custom admin site title"""
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'LEON GAMES PRO')
    
    def test_all_models_registered(self):
        """Test all models are registered in admin"""
        response = self.client.get(reverse('admin:index'))
        
        # Check all models are visible
        self.assertContains(response, 'Predictions')
        self.assertContains(response, 'Teams')
        self.assertContains(response, 'Matches')
        self.assertContains(response, 'Leagues')
        self.assertContains(response, 'User profiles')
        self.assertContains(response, 'Subscriptions')
        self.assertContains(response, 'Billing usages')


class AdminPermissionsTest(TestCase):
    """Test admin permissions and security"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@gmail.com',
            password='pass123'
        )
    
    def test_regular_user_cannot_access_admin(self):
        """Test regular users are blocked from admin"""
        self.client.login(username='regular', password='pass123')
        
        # Try to access various admin pages
        urls = [
            reverse('admin:index'),
            reverse('admin:predictor_prediction_changelist'),
            reverse('admin:predictor_userprofile_changelist'),
            reverse('admin:predictor_subscription_changelist'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
    
    def test_admin_user_can_access_all(self):
        """Test admin users can access all admin pages"""
        self.client.login(username='admin', password='admin123')
        
        urls = [
            reverse('admin:index'),
            reverse('admin:predictor_prediction_changelist'),
            reverse('admin:predictor_userprofile_changelist'),
            reverse('admin:predictor_subscription_changelist'),
            reverse('admin:predictor_team_changelist'),
            reverse('admin:predictor_match_changelist'),
            reverse('admin:predictor_league_changelist'),
            reverse('admin:predictor_billingusage_changelist'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


# Test runner configuration
if __name__ == '__main__':
    import unittest
    unittest.main()
