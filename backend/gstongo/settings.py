"""
Django settings for GSTONGO project.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-dev-key-change-in-production'
DEBUG = True

ALLOWED_HOSTS = ['gstongo.com', 'www.gstongo.com', '127.0.0.1', 'localhost', '*']

# Applications
INSTALLED_APPS = [
    'unfold',  # must be before django.contrib.admin
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_otp',

    # Local apps
    'apps.users',
    'apps.core',
    'apps.gst_filing',
    'apps.notifications',
    'apps.invoices',
    'apps.payments',
    'apps.admin_portal',
]

UNFOLD = {
    "SITE_TITLE": "GSTONGO Admin",
    "SITE_SYMBOL": "speed", # font awesome symbol
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "244 247 254",
            "100": "231 237 252",
            "200": "205 219 249",
            "300": "170 192 244",
            "400": "128 156 238",
            "500": "99 123 232",
            "600": "79 96 219",
            "700": "67 79 203",
            "800": "58 66 166",
            "900": "51 58 133",
            "950": "33 36 78",
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gstongo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'gstongo.wsgi.application'

# =========================================================
# DATABASE (HARDCODED AWS RDS)
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gstongo',
        'USER': 'gstongo',
        'PASSWORD': 'gstongoadmin',
        'HOST': 'gstongo-db.c5igmwgccjat.eu-north-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# =========================================================
# AUTH
# =========================================================

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC & MEDIA
# =========================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================
# DRF
# =========================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# =========================================================
# JWT
# =========================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'SIGNING_KEY': SECRET_KEY,
}

# =========================================================
# CORS / CSRF
# =========================================================

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://gstongo.com',
    'https://www.gstongo.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://gstongo.com',
    'https://www.gstongo.com',
]

# =========================================================
# EMAIL
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'viviztechnologies@gmail.com'
EMAIL_HOST_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD'
DEFAULT_FROM_EMAIL = 'GSTONGO <viviztechnologies@gmail.com>'

# =========================================================
# LOGGING
# =========================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# =========================================================
# FRONTEND
# =========================================================

FRONTEND_URL = 'https://gstongo.com'
