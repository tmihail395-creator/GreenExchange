"""Django settings for website project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Режим работы ----------
# Локально DEBUG включён по умолчанию, на хостинге задаётся DEBUG=0
DEBUG = os.environ.get('DEBUG', '1') == '1'

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-key-change-me'
    else:
        raise RuntimeError('SECRET_KEY environment variable is required when DEBUG=0')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    f'https://{h}' for h in ALLOWED_HOSTS if h not in ('localhost', '127.0.0.1')
]


# ---------- Приложения ----------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'helloweb',
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

ROOT_URLCONF = 'website.urls'

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
                'helloweb.context_processors.market',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# ---------- База данных ----------
# На хостинге задаётся DATABASE_URL (PostgreSQL), локально используется SQLite
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------- Пароли ----------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------- Язык и время ----------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------- Статика ----------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ---------- Боевой режим ----------
if not DEBUG:
    # WhiteNoise раздаёт CSS и JS прямо из Django
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }

    # Кеш в базе общий для всех процессов gunicorn (нужна команда createcachetable)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }

    # HTTPS и безопасные cookie
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600   # потом можно увеличить до года


# ---------- Логи (видны в панели хостинга) ----------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}


# ---------- Вход и регистрация ----------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# 1: новые аккаунты неактивны, пока админ не одобрит их в админке
REGISTRATION_REQUIRES_APPROVAL = os.environ.get('REGISTRATION_REQUIRES_APPROVAL', '0') == '1'


# ---------- Почта ----------
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


# ---------- Ключ CoinGecko ----------
# Сначала из переменной окружения (хостинг), потом из local_settings.py (ваш компьютер)
COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY', '')
if not COINGECKO_API_KEY:
    try:
        from .local_settings import COINGECKO_API_KEY
    except ImportError:
        pass
