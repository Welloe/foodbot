import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Security Settings
SECRET_KEY = 'django-insecure-o)c1%hms*$ya)630sse&0w5pxpnwb^6odbtpd8s_eu*_b1$e*u'  # ⚠️ Replace in production!
DEBUG = False  # ⚠️ Set to False in production

ALLOWED_HOSTS = [
    '*',  # ⚠️ Use specific domains/IPs in production
    'foodbot-app-hcd0d3cza6akarek.westeurope-01.azurewebsites.net',
]

CSRF_TRUSTED_ORIGINS = [
    'https://foodbot-app-hcd0d3cza6akarek.westeurope-01.azurewebsites.net'
]


# Authentication URLs
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'


# Installed Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',

    # Local apps
    'chatbot',
]


# Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Serve static files efficiently
    'whitenoise.middleware.WhiteNoiseMiddleware',
]


# REST Framework Defaults
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# URL Configuration
ROOT_URLCONF = 'backend.urls'


# Template Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI Application
WSGI_APPLICATION = 'backend.wsgi.application'


# Database Configuration (SQL Server)
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'foodbot',
        'USER': 'foodbotadmin',
        'PASSWORD': 'SuperStrongP@ssw0rd!',
        'HOST': 'foodbot-db-server.database.windows.net',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}


# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static Files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default Primary Key Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'