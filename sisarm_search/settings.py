from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# === RUTAS Y SEGURIDAD ===
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-temporal-para-desarrollo')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# === APLICACIONES INSTALADAS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'partidas',
    'widget_tweaks',
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # ✔ Primero este
    'partidas.middleware.VerificarLicenciaMiddleware',           # ✔ Luego tu middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === CONFIGURACIÓN DE URLS Y TEMPLATES ===
ROOT_URLCONF = 'sisarm_search.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Si colocas templates fuera de apps, agrégalos aquí
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'partidas.context_processors.license_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'sisarm_search.wsgi.application'

# === BASE DE DATOS ===
import dj_database_url

# En producción usa DATABASE_URL (proporcionada por Railway)
# En desarrollo usa SQLite
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'), conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# === USUARIO PERSONALIZADO ===
AUTH_USER_MODEL = 'partidas.Usuario'

# === VALIDADORES DE CONTRASEÑA ===
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# === LOCALIZACIÓN ===
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# === ARCHIVOS ESTÁTICOS ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media (archivos subidos por usuarios / referencias)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === AUTENTICACIÓN Y REDIRECCIONES ===
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/inicio/'
              # Redirección si no está autenticado

# === AUTO FIELD POR DEFECTO PARA MODELOS ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Soporte / WhatsApp (puedes sobreescribir en settings de producción) ---
# Número por defecto en formato internacional (sin +). Se usa para generar enlaces wa.me.
SUPPORT_WHATSAPP_NUMBER = '59177682918'
# Texto por defecto para el mensaje en WhatsApp (no codificado; el backend hará urlencode si es necesario).
SUPPORT_WHATSAPP_TEXT = 'Hola, tengo una consulta sobre Sisarm.'

# === Email ===
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Configuración de depuración de correo
if not DEBUG:
    # Seguridad en producción
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# === LOGGING - enviar logs a stdout (Railway/Heroku style) ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOGLEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'partidas': {
            'handlers': ['console'],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
    }
}
