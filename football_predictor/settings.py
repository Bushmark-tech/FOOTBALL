"""
Django settings for football_predictor project.
"""

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
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


# Add django-allauth if installed (for Google OAuth)
try:
    import allauth
    INSTALLED_APPS.extend([
        'django.contrib.sites',  # Required for Google OAuth
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
    ])
except ImportError:
    pass  # django-allauth not installed, skip Google OAuth

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add allauth middleware if installed
try:
    import allauth
    MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')
except ImportError:
    pass

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

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Redis Cache Configuration
# Use Redis if available (from Render Redis service), otherwise fallback to database
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')

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
TIME_ZONE = 'UTC'
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

# Django Allauth Configuration (only if installed)
try:
    import allauth
    SITE_ID = 1
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]
    
    # Allauth Settings
    ACCOUNT_LOGIN_METHODS = {'email', 'username'}
    ACCOUNT_SIGNUP_FIELDS = ['email', 'username*', 'password1*', 'password2*']
    ACCOUNT_EMAIL_VERIFICATION = 'none'
    LOGIN_URL = '/login/'
    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/login/'
    
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
except ImportError:
    # django-allauth not installed, use default authentication
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
    ]
    LOGIN_URL = '/login/'
    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/login/'
    SITE_ID = 1

# Subscription Settings
FREE_MATCHES_LIMIT = 3
SUBSCRIPTION_PRICE_USD = 2.00
SUBSCRIPTION_PRICE_KSH = 200.00
SUBSCRIPTION_DURATION_DAYS = 30

# M-Pesa Settings
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'r2IXj8KBeM6QbFPPQTzdmPpme1anleTRobqzsZgbAGLf3i4t')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'RUerdbN3pWXGbi3fp2PDicrrTQetWwtzhpZN34xGzITJR8qDhBAZxOaLNeVkaGrz')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'sandbox') 

# CSRF Settings
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = False  # Must be False to allow JavaScript to read the token
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]

# Session Settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# FastAPI Service Configuration
FASTAPI_URL = os.environ.get('FASTAPI_URL', 'http://127.0.0.1:8001')
FASTAPI_TIMEOUT = int(os.environ.get('FASTAPI_TIMEOUT', '30'))  # seconds

# Google Analytics
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')