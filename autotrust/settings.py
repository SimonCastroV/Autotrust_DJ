from pathlib import Path
import os
from decimal import Decimal

import dj_database_url
from django.contrib.messages import constants as messages

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
_env_truthy_values = {"1", "true", "yes", "on"}


def _env_list(setting_name):
    """
    Parse comma-separated environment variables into a clean list.
    """
    return [item.strip() for item in os.getenv(setting_name, "").split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    'django-insecure-=$qd#&3a#k41%jdc53=&=yo((u-)^k=fx=--69ffkev+es#nz(',
)
DEBUG = os.getenv("DJANGO_DEBUG", "True").strip().lower() in _env_truthy_values
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# --- LANGUAGE / TIME ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'vehicles',
    'account',

    # Utilidades
    'django.contrib.humanize',
    'channels',
    'chatt',
]
# --- AUTH ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLS & WSGI ---
ROOT_URLCONF = 'autotrust.urls'
WSGI_APPLICATION = 'autotrust.wsgi.application'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Carpeta general de templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]


ASGI_APPLICATION = 'autotrust.asgi.application'

# --- CHANNELS / WEBSOCKETS ---
_redis_url = os.getenv("REDIS_URL")
if _redis_url:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [_redis_url]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
# --- DATABASE ---
_database_url = os.getenv("DATABASE_URL")
if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=int(os.getenv("DJANGO_DB_CONN_MAX_AGE", "60")),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- STATIC & MEDIA ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Crea la carpeta si no existe para evitar el warning
STATIC_ROOT = Path(os.getenv("DJANGO_STATIC_ROOT") or (BASE_DIR / 'staticfiles'))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- VARIABLES DEL PROYECTO ---
SALES_TAX = Decimal("0.19")  # 19% de IVA por defecto

# URL del servicio aliado a consumir en /vehicles/aliados/
# Cambia esta URL por la del equipo aliado cuando la tengas:
PARTNER_PRODUCTS_URL = "https://equipo2.ejemplo/api/productos/"
# Ejemplo local alternativo:
# PARTNER_PRODUCTS_URL = "http://127.0.0.1:8001/api/aliados/"

# --- DEFAULT PK FIELD ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
