"""
Simple admin verification test
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class SimpleAdminTest(TestCase):
    """Simple test to verify admin is working"""
    
    def setUp(self):
        """Set up admin user"""
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
    
    def test_admin_login_works(self):
        """Test admin login"""
        logged_in = self.client.login(username='admin', password='admin123')
        self.assertTrue(logged_in, "Admin should be able to login")
        print("✓ Admin login works")
    
    def test_admin_index_accessible(self):
        """Test admin index page"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200, "Admin index should be accessible")
        print("✓ Admin index accessible")
    
    def test_admin_models_registered(self):
        """Test all models are registered"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        
        # Check for key models
        models = ['Predictions', 'Teams', 'Matches', 'Leagues', 'User profiles', 'Subscriptions']
        for model in models:
            self.assertContains(response, model, msg_prefix=f"{model} should be in admin")
            print(f"✓ {model} registered in admin")
    
    def test_admin_customization(self):
        """Test admin customization"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        self.assertContains(response, 'LEON GAMES PRO', msg_prefix="Custom admin title should be present")
        print("✓ Admin customization working")


if __name__ == '__main__':
    import unittest
    unittest.main()
