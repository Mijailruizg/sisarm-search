"""
Configuración de producción para Railway.
Importa desde settings.py y sobrescribe valores específicos para producción.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Import opcional: dj_database_url puede no estar presente en el entorno de edición
try:
    import dj_database_url
except Exception:
    dj_database_url = None

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
ALLOWED_HOSTS = [
    'mxtoday.online',
    'www.mxtoday.online',
    '*.railway.app',
    'localhost',
]

# SECRET_KEY desde variable de entorno (Railway la configura automáticamente)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CAMBIAR-EN-PRODUCCION')

# ============================================================
# BASE DE DATOS (PostgreSQL en Railway)
# ============================================================
# Railway proporciona DATABASE_URL como variable de entorno
DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback a SQLite si no hay DATABASE_URL
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

# Configurar WhiteNoise para servir archivos estáticos en producción
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Compresión de archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos media (subidas de usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# SEGURIDAD HTTPS Y COOKIES
# ============================================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
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
CSRF_TRUSTED_ORIGINS = [
    'https://mxtoday.online',
    'https://www.mxtoday.online',
]

# Cabeceras de seguridad adicionales
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

print("✓ Configuración de producción cargada correctamente")
