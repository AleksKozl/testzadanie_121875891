from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure')

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'parser.apps.ParserConfig',
    'products.apps.ProductsConfig',

    'rest_framework',
    'django_filters',
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

ROOT_URLCONF = 'wildberries_parser_tz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wildberries_parser_tz.wsgi.application'


# Database

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DB_POSTGRESQL_NAME = os.getenv('DB_POSTGRESQL_NAME')
DB_POSTGRESQL_USER = os.getenv('DB_POSTGRESQL_USER')
DB_POSTGRESQL_PASSWORD = os.getenv('DB_POSTGRESQL_PASSWORD')
DB_POSTGRESQL_HOST = os.getenv('DB_POSTGRESQL_HOST')
DB_POSTGRESQL_PORT = os.getenv('DB_POSTGRESQL_PORT')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_POSTGRESQL_NAME,
        'USER': DB_POSTGRESQL_USER,
        'PASSWORD': DB_POSTGRESQL_PASSWORD,
        'HOST': DB_POSTGRESQL_HOST,
        'PORT': DB_POSTGRESQL_PORT,
    }
}

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        }
    }

    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    DEBUG = False


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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Celery settings
REDIS_CELERY_PASSWORD = os.getenv('REDIS_CELERY_PASSWORD')
REDIS_CELERY_HOST = os.getenv('REDIS_CELERY_HOST')
REDIS_CELERY_PORT = os.getenv('REDIS_CELERY_PORT')
REDIS_CELERY_DB_NUMB_BROKER = os.getenv('REDIS_CELERY_DB_NUMB', '0')
REDIS_CELERY_DB_NUMB_BACKEND = os.getenv('REDIS_CELERY_DB_NUMB', '1')

CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL',
    default='redis://:{password}@{host}:{port}/{db_numb}'.format(
        password=REDIS_CELERY_PASSWORD,
        host=REDIS_CELERY_HOST,
        port=REDIS_CELERY_PORT,
        db_numb=REDIS_CELERY_DB_NUMB_BROKER,
    )
)
CELERY_RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND',
    default='redis://:{password}@{host}:{port}/{db_numb}'.format(
        password=REDIS_CELERY_PASSWORD,
        host=REDIS_CELERY_HOST,
        port=REDIS_CELERY_PORT,
        db_numb=REDIS_CELERY_DB_NUMB_BACKEND,
    )
)
