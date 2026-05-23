
from pathlib import Path

import os
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
     'rest_framework',
     'rest_framework_simplejwt',
     'rest_framework_simplejwt.token_blacklist',
     'django_filters',
     'drf_yasg',

    # local apps

    'apps.users', # Handles  User registration ,Login , logout  
    'apps.flashcards' , #  Manages flashcards,decks,reviews, and learning logic 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'users.CustomUser'








"""
Django password validators 
"""

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




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework_simplejwt.authentication.JWTAuthentication' # use simple JWT
    ],
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.IsAuthenticated',

    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # For anonymous users
        "utils.throttles.AdminExemptUserRateThrottle",  # For authenticated users (exempts staff & superusers)
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/minute",  # Limit for anonymous users
        "user": "180/minute",  # Limit for authenticated users (except staff & superusers)
    },
}

SIMPLE_JWT ={
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME':timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':True, 
    'BLACKLIST_AFTER_ROTATION':True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': None,  # Use Django's SECRET_KEY for signing & config this later on separate environment-specific settings files due to security reasons
    'AUTH_HEADER_TYPES': ('Bearer',),
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


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

WSGI_APPLICATION = 'config.wsgi.application'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static') # To run python manage.py collectstatic on depolyment for swagger docs


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGS_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    "version":1,
    "disable_existing_loggers":False,
    "formatters":{
        'verbose':{
            'format':'[{levelname}] [{asctime}] [{module}] [{pathname}] [{lineno}] >> {message}',
            'style':'{',
        },
        'simple':{
            'format':'[{levelname}] >> {message}',
            'style':'{',
        },

    },
    "handlers":{
        "console":{
            "level": None, # Config later
            "class":"logging.StreamHandler",
            "formatter":"simple",

        },
        "file":{
            'level':None,
            "class":"logging.handlers.RotatingFileHandler",
            "filename":None,# config later 
            "maxBytes":1024*1024 * 5, # 5 MB
            "backupCount":5,
            "formatter":'verbose',

        },
     
    },
    "root":{
        "handlers":["console"],
        "level":"WARNING",
    

    },
    "loggers":{
         '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': None,  # Config later
            'propagate': True,
        },
        "django":{
            "handlers":["console"],
            "level":os.getenv("DJANGO_LOG_LEVEL","INFO"),
            "propgate":False,
        },
        "apps.users":{
            "handlers":["console","file"],
            "level":None,  # Config later
            "propagate":False,
        },
        "apps.flashcards":{
            'handlers':["console","file"],
            "level":None, # Config later
            "propagate":False,

        },

    },

}


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

