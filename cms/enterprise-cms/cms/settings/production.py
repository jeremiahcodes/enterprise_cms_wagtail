import os
import dj_database_url
from .base import *

DEBUG = False

# Add WhiteNoise middleware for static files
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# CSRF trusted origins for Azure App Service
CSRF_TRUSTED_ORIGINS = [
    'https://appwagtail-eku4qbynnabok.azurewebsites.net',
    'https://*.azurewebsites.net',
]

# Database configuration for PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True
        )
    }
else:
    # Fallback to SQLite for now to get the app running
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }

# Azure Blob Storage configuration
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')

# Serve static files from container, media files from Azure Storage
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Static files served from container using WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
    # Use Azure Blob Storage for media files only
    STORAGES["default"] = {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "azure_container": "media",
            "account_name": AZURE_ACCOUNT_NAME,
            "account_key": AZURE_ACCOUNT_KEY,
            "overwrite_files": True,
            "azure_ssl": True,
        },
    }
    
    # Media files configuration with Azure Blob Storage (private)
    AZURE_MEDIA_CONTAINER = 'media'
    # Serve media files through Django instead of direct Azure URLs
    MEDIA_URL = '/media/'
    
    # Custom storage class for private Azure media files
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
else:
    # Fallback to local storage for media files too
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/app/media'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = False  # Set to False for Azure App Service testing
CSRF_COOKIE_SECURE = False     # Set to False for Azure App Service testing

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'wagtail': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Application Insights configuration
APPLICATIONINSIGHTS_CONNECTION_STRING = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
if APPLICATIONINSIGHTS_CONNECTION_STRING:
    INSTALLED_APPS.append('applicationinsights.django')
    
    # Application Insights middleware
    MIDDLEWARE.insert(0, 'applicationinsights.django.ApplicationInsightsMiddleware')
    
    APPLICATION_INSIGHTS = {
        'ikey': APPLICATIONINSIGHTS_CONNECTION_STRING,
    }

# Cache configuration (optional - using local memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email configuration (you may want to configure this for your email provider)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from .local import *
except ImportError:
    pass
