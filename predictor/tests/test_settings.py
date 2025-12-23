"""
Tests for settings and configuration.
"""
from django.test import TestCase, override_settings
from django.conf import settings


class SettingsTest(TestCase):
    """Test cases for Django settings."""
    
    def test_debug_setting(self):
        """Test that DEBUG setting exists."""
        self.assertIn('DEBUG', dir(settings))
    
    def test_secret_key_setting(self):
        """Test that SECRET_KEY is set."""
        self.assertIn('SECRET_KEY', dir(settings))
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertGreater(len(settings.SECRET_KEY), 0)
    
    def test_installed_apps(self):
        """Test that predictor app is installed."""
        self.assertIn('predictor', settings.INSTALLED_APPS)
    
    def test_database_config(self):
        """Test database configuration."""
        self.assertIn('DATABASES', dir(settings))
        self.assertIn('default', settings.DATABASES)
    
    def test_static_files_config(self):
        """Test static files configuration."""
        self.assertIn('STATIC_URL', dir(settings))
        self.assertIn('STATIC_ROOT', dir(settings))


# Override cache settings for tests to use dummy cache
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class SettingsWithDummyCacheTest(TestCase):
    """Test settings with dummy cache for tests that don't need Redis."""
    pass
