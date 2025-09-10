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
print(f"DEBUG: DATABASE_URL = '{DATABASE_URL}' (length: {len(DATABASE_URL) if DATABASE_URL else 0})")

# Also try individual database environment variables as fallback
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

print(f"DEBUG: Individual DB vars - HOST: {DB_HOST}, NAME: {DB_NAME}, USER: {DB_USER}, PASSWORD: {'***' if DB_PASSWORD else None}")

# Check if DATABASE_URL is properly formatted (not a KeyVault reference)
if DATABASE_URL and DATABASE_URL.strip() and DATABASE_URL.startswith(('postgresql://', 'postgres://')):
    try:
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True
            )
        }
        # Ensure SSL is enabled for Azure PostgreSQL
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }
        print("DEBUG: Using PostgreSQL database from DATABASE_URL")
    except Exception as e:
        print(f"ERROR: Failed to parse DATABASE_URL: {e}")
        # Fallback to individual environment variables
        if all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': DB_NAME,
                    'USER': DB_USER,
                    'PASSWORD': DB_PASSWORD,
                    'HOST': DB_HOST,
                    'PORT': '5432',
                    'OPTIONS': {
                        'sslmode': 'require',
                    },
                }
            }
            print("DEBUG: Using PostgreSQL database from individual environment variables")
        else:
            # Final fallback to SQLite
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '/tmp/db.sqlite3',
                }
            }
            print("DEBUG: Fell back to SQLite due to DATABASE_URL parse error and missing individual vars")
elif DATABASE_URL and ('KeyVault' in str(DATABASE_URL) or DATABASE_URL.startswith('@Microsoft')):
    print(f"WARNING: DATABASE_URL appears to be an unresolved KeyVault reference: {DATABASE_URL}")
    # Try individual environment variables as fallback
    if all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': DB_NAME,
                'USER': DB_USER,
                'PASSWORD': DB_PASSWORD,
                'HOST': DB_HOST,
                'PORT': '5432',
                'OPTIONS': {
                    'sslmode': 'require',
                },
            }
        }
        print("DEBUG: Using PostgreSQL database from individual environment variables (KeyVault fallback)")
    else:
        # Fallback to SQLite when KeyVault reference is not resolved
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/db.sqlite3',
            }
        }
        print("DEBUG: Using SQLite due to unresolved KeyVault reference")
else:
    # Try individual environment variables first
    if all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': DB_NAME,
                'USER': DB_USER,
                'PASSWORD': DB_PASSWORD,
                'HOST': DB_HOST,
                'PORT': '5432',
                'OPTIONS': {
                    'sslmode': 'require',
                },
            }
        }
        print("DEBUG: Using PostgreSQL database from individual environment variables")
    else:
        # Final fallback to SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/tmp/db.sqlite3',
            }
        }
        print("DEBUG: Using SQLite (no valid DATABASE_URL or individual vars found)")

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
            "expiration_secs": 3600,  # URLs expire after 1 hour
            "custom_domain": None,  # Don't use custom domain for private storage
        },
    }
    
    # Media files configuration with Azure Blob Storage (private)
    AZURE_MEDIA_CONTAINER = 'media'
    # Serve media files through Django instead of direct Azure URLs for private storage
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
