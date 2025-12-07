"""
Configuración de producción para Railway.
Importa desde settings.py y sobrescribe valores específicos para producción.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================
# IMPORTAR CONFIGURACIÓN BASE (desarrollo)
# ============================================================
from .settings import *

# ============================================================
# SEGURIDAD Y DEBUG
# ============================================================
DEBUG = False
# ----------------------------
# Ajustes de producción
# ----------------------------
DEBUG = False

# ALLOWED_HOSTS configurable vía variable de entorno (coma-separada)
allowed = os.getenv('ALLOWED_HOSTS', 'mxtoday.online,www.mxtoday.online,localhost')
ALLOWED_HOSTS = [h.strip() for h in allowed.split(',') if h.strip()]

# SECRET_KEY desde variable de entorno (Heroku/Railway la deben proveer)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CAMBIAR-EN-PRODUCCION')

# ============================================================
# BASE DE DATOS (Heroku / Railway usan DATABASE_URL)
# ============================================================
DATABASE_URL = os.getenv('DATABASE_URL', '')
try:
    import dj_database_url
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
    else:
        # fallback a sqlite para desarrollo local cuando no hay DATABASE_URL
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except Exception:
    # Si dj_database_url no está instalado en el entorno local, usar sqlite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Insertar WhiteNoise si no está ya presente
whitenoise_path = 'whitenoise.middleware.WhiteNoiseMiddleware'
if whitenoise_path not in MIDDLEWARE:
    # insert after SecurityMiddleware (pos 1) si existe; si no, al inicio
    try:
        sec_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        MIDDLEWARE.insert(sec_index + 1, whitenoise_path)
    except ValueError:
        MIDDLEWARE.insert(0, whitenoise_path)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos media (subidas de usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# SEGURIDAD HTTPS Y COOKIES
# ============================================================
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Permitir que Heroku (o proxies) informen HTTPS correctamente
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Content Security Policy y orígenes de recursos mínimos — ajustar según necesidad
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    'style-src': ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    'img-src': ("'self'", "data:", "https:"),
}

# ============================================================
# LOGGING PARA PRODUCCIÓN
# ============================================================
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
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================
# OTRAS CONFIGURACIONES
# ============================================================
# Permitir hosts CSRF desde Railway
# CSRF_TRUSTED_ORIGINS configurable (coma-separados). Si no, por defecto incluir dominio principal.
csrf_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_env:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in csrf_env.split(',') if u.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS if h and not h.startswith('*.')]

# Cabeceras de seguridad adicionales
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1 año por defecto
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('true', '1', 'yes')
SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() in ('true', '1', 'yes')
