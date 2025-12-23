"""
Production middleware for rate limiting and security.
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware.
    For production, consider using django-ratelimit package.
    """
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100  # requests per window
    RATE_LIMIT_WINDOW = 60  # seconds
    
    def process_request(self, request):
        if not self.RATE_LIMIT_ENABLED:
            return None
            
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{ip}'
        
        # Get current request count
        requests = cache.get(cache_key, 0)
        
        if requests >= self.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': self.RATE_LIMIT_WINDOW
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, requests + 1, self.RATE_LIMIT_WINDOW)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses."""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server header
        if 'Server' in response:
            del response['Server']
        
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor request performance and log slow queries."""
    
    SLOW_REQUEST_THRESHOLD = 1.0  # seconds
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            if duration > self.SLOW_REQUEST_THRESHOLD:
                logger.warning(
                    f"Slow request: {request.path} took {duration:.2f}s",
                    extra={
                        'path': request.path,
                        'method': request.method,
                        'duration': duration,
                        'ip': request.META.get('REMOTE_ADDR'),
                    }
                )
            
            # Add performance header
            response['X-Process-Time'] = f'{duration:.3f}'
        
        return response

