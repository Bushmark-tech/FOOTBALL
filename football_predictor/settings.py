"""
Django settings for football_predictor project.
"""

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ... (rest of imports)

# ... (skip to keys)


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
# For local development, set DEBUG=True to see detailed errors
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'  # Changed default to True for local dev

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'predictor',
]


# Add django-allauth (for Google OAuth)
INSTALLED_APPS.extend([
    'django.contrib.sites',  # Required for Google OAuth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
])

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'football_predictor.security_middleware.ScannerBlockerMiddleware', # Custom Bot Blocker
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add allauth middleware
MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')

ROOT_URLCONF = 'football_predictor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'football_predictor.wsgi.application'

# Database
# Use PostgreSQL on Render, SQLite for local development
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Check if we are running on Render
IS_RENDER = os.environ.get('RENDER')

if IS_RENDER or not DEBUG:
    # In production (Render), we MUST use PostgreSQL
    # EXCEPTION: Allow build process (collectstatic) to run without DB
    import sys
    is_building = 'collectstatic' in sys.argv or 'migrate' in sys.argv or 'createcachetable' in sys.argv
    
    if not os.environ.get('DATABASE_URL') and not is_building:
        raise ImproperlyConfigured(
            "DATABASE_URL environment variable not set. "
            "You cannot run with SQLite in production as data will be lost on every deploy."
        )
    
    if os.environ.get('DATABASE_URL'):
        DATABASES = {
            'default': dj_database_url.config(
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        # Fallback for build process only
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

else:
    # Local development - nice fallback to SQLite if Postgres not set
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

print(f"Active Database Engine: {DATABASES['default']['ENGINE']}")

# Redis Cache Configuration
# Use Redis if available (from Render Redis service), otherwise fallback to database
REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL and not DEBUG:
    # Use Redis cache in production if available
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,  # Don't crash if Redis is down
            },
            'KEY_PREFIX': 'football_predictor',
            'TIMEOUT': 300,  # 5 minutes default timeout
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Fallback to database cache/sessions
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for serving static files on Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django Allauth Configuration
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth Settings
# Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Email Settings
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Football Predictor <noreply@football-predictor.com>')

# Site URL for emails
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
if IS_RENDER:
    SITE_URL = 'https://football-o48u.onrender.com'

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}

# Skip the intermediate "Sign in with Google" confirmation page
SOCIALACCOUNT_LOGIN_ON_GET = True

# Subscription Settings
FREE_MATCHES_LIMIT = 1
SUBSCRIPTION_PRICE_USD = 2.00
SUBSCRIPTION_PRICE_KSH = 200.00
SUBSCRIPTION_DURATION_DAYS = 30

# M-Pesa Settings
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '5699046')  # Till Number
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'sandbox') 

if MPESA_ENVIRONMENT == 'production':
    MPESA_ACCESS_TOKEN_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
else:
    MPESA_ACCESS_TOKEN_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest' 

# CSRF Settings
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = False  # Must be False to allow JavaScript to read the token
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://football-o48u.onrender.com,https://leon-football.com,https://www.leon-football.com').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]

# Session Settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_NAME = 'sessionid_v2'  # Rotate cookie to fix "Session data corrupted" errors

# FastAPI Service Configuration
FASTAPI_URL = os.environ.get('FASTAPI_URL', 'http://127.0.0.1:8001')
FASTAPI_TIMEOUT = int(os.environ.get('FASTAPI_TIMEOUT', '30'))  # seconds

# Google Analytics
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')

# Production Security Settings
if IS_RENDER:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Secure Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True