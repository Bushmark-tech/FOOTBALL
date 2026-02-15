"""
Production Settings for High-Traffic Scalability

This file contains optimized settings for handling millions of users.
Use this by setting: export DJANGO_SETTINGS_MODULE=football_predictor.settings_production
"""

from .settings import *
import os

# Security Settings
DEBUG = False

# ALLOWED_HOSTS - MUST be configured in production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,leon-football.com,www.leon-football.com').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

# Validate ALLOWED_HOSTS is set in production
# if not ALLOWED_HOSTS:
#     raise ValueError(
#         "ALLOWED_HOSTS must be set in production. "
#         "Set environment variable: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com"
#     )

# Validate all required environment variables in production
REQUIRED_ENV_VARS = {
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    'DATABASE_URL': os.environ.get('DATABASE_URL'),
    # 'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS'),  # We have defaults now
}

missing_vars = [var for var, value in REQUIRED_ENV_VARS.items() if not value]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables for production: {', '.join(missing_vars)}. "
        f"Please set these in your environment or .env file."
    )

# Database - Use DATABASE_URL if provided, else fallback to SQLite for local tests
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# For even better performance, use PgBouncer or Django-DB-Geventpool
# Example with django-db-geventpool:
# DATABASES['default']['ENGINE'] = 'django_db_geventpool.backends.postgresql_psycopg2'
# DATABASES['default']['POOL_SIZE'] = 20

# Redis Cache Configuration (for high-traffic caching)
if os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_CLASS': 'redis.connection.HiredisParser',  # Faster C-based parser
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',  # Compress cached data
                'IGNORE_EXCEPTIONS': True,  # Don't crash if Redis is down
            },
            'KEY_PREFIX': 'football_predictor',
            'VERSION': 1,
            'TIMEOUT': 300,  # 5 minutes default
        },
        # Separate cache for sessions
        'session': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            },
            'TIMEOUT': 86400,  # 24 hours for sessions
        },
    }
else:
    # Fallback for local testing without Redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'session-snowflake',
        }
    }

# Use Redis for session storage if URL is present, otherwise fallback to cache
if os.environ.get('REDIS_URL'):
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'session'
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Static files optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Security enhancements
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = 0  # Disabled by default for local-prod tests
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'predictor': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration for error notifications
ADMINS = [('Admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com'))]
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@example.com')

# Email Configuration - Ensure SMTP is used in production
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Football Predictor <noreply@leon-football.com>')

# Log email configuration (without exposing password)
print("=" * 80)
print("EMAIL CONFIGURATION (Production)")
print("=" * 80)
print(f"EMAIL_BACKEND: {EMAIL_BACKEND}")
print(f"EMAIL_HOST: {EMAIL_HOST}")
print(f"EMAIL_PORT: {EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'SET (' + str(len(EMAIL_HOST_PASSWORD)) + ' chars)' if EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {DEFAULT_FROM_EMAIL}")
print("=" * 80)

# Warn if email is not properly configured
if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("WARNING: Using console email backend in production!")
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    print("WARNING: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set!")

# Database query optimization
# Log slow queries (queries taking more than 0.5 seconds)
if DEBUG:
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }

# Rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Celery configuration for background tasks (optional but recommended)
# CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'UTC'

# Auto-cleanup scheduling (run cleanup_predictions command daily)
# Add to crontab: 0 2 * * * cd /path/to/project && python manage.py cleanup_predictions

# FastAPI Service Configuration (Production)
FASTAPI_URL = os.environ.get('FASTAPI_URL', 'http://localhost:8001')
FASTAPI_TIMEOUT = int(os.environ.get('FASTAPI_TIMEOUT', '30'))  # seconds

# Performance monitoring (optional - add New Relic, Sentry, etc.)
# SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
# if SENTRY_DSN:
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,  # Sample 10% of transactions
#     )
