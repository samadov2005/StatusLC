import os
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required in production")

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

if DEBUG and 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'core',
    'accounts',
    'telegram_bot',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000'
    ).split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000'
    ).split(',')
    if origin.strip()
]

# Security settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', str(not DEBUG)).lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', str(not DEBUG)).lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', str(not DEBUG)).lower() == 'true'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

ROOT_URLCONF = 'statuslc.urls'

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

WSGI_APPLICATION = 'statuslc.wsgi.application'

def build_database_config():
    """Build database settings from env, defaulting to local SQLite."""
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme not in ('postgres', 'postgresql'):
            raise ValueError("DATABASE_URL must use postgres:// or postgresql://")
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': unquote(parsed.path.lstrip('/')),
            'USER': unquote(parsed.username or ''),
            'PASSWORD': unquote(parsed.password or ''),
            'HOST': parsed.hostname or 'localhost',
            'PORT': str(parsed.port or 5432),
        }

    if os.environ.get('POSTGRES_DB'):
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }

    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


DATABASES = {
    'default': build_database_config(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'uz')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Tashkent')

STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.OrderingFilter',
    ],
}

# Logging Configuration
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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Jazzmin admin theme settings
JAZZMIN_SETTINGS = {
    "site_title": "StatusLC Admin",
    "site_header": "StatusLC",
    "site_brand": "StatusLC",
    "welcome_sign": "Welcome to StatusLC admin panel",
    "search_model": ['accounts.Profile', 'core.Student', 'core.Group'],
    "show_statistics": True,
    "custom_css": None,
    "custom_js": None,
    "userswitcher_enabled": False,
}

# Authentication redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

