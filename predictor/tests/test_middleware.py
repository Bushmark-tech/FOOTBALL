"""
Tests for custom middleware.
"""
from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse
from predictor.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    PerformanceMonitoringMiddleware
)


# Override cache settings for middleware tests
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class MiddlewareTestBase(TestCase):
    """Base class for middleware tests with test-friendly cache settings."""
    pass


class RateLimitMiddlewareTest(MiddlewareTestBase):
    """Test cases for rate limiting middleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda req: HttpResponse())
    
    def test_rate_limit_allows_normal_requests(self):
        """Test that normal requests are allowed."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # None means continue
    
    def test_rate_limit_skips_admin(self):
        """Test that admin paths are not rate limited."""
        request = self.factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_rate_limit_skips_static(self):
        """Test that static files are not rate limited."""
        request = self.factory.get('/static/css/style.css')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)


class SecurityHeadersMiddlewareTest(MiddlewareTestBase):
    """Test cases for security headers middleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda req: HttpResponse())
    
    def test_security_headers_added(self):
        """Test that security headers are added."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, HttpResponse())
        
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Referrer-Policy', response)


class PerformanceMonitoringMiddlewareTest(MiddlewareTestBase):
    """Test cases for performance monitoring middleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        # Create middleware with a callable that returns HttpResponse
        def get_response(request):
            return HttpResponse()
        self.middleware = PerformanceMonitoringMiddleware(get_response)
    
    def test_performance_header_added(self):
        """Test that performance header is added."""
        request = self.factory.get('/')
        # Process request first to set start time
        self.middleware.process_request(request)
        response = self.middleware.process_response(request, HttpResponse())
        
        self.assertIn('X-Process-Time', response)
        # Should be a float string
        self.assertIsInstance(float(response['X-Process-Time']), float)

