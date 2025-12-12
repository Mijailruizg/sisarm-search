

from pathlib import Path
import os
from dotenv import load_dotenv


try:
    import dj_database_url
except Exception:
    dj_database_url = None


load_dotenv()


from .settings import *


DEBUG = False
ALLOWED_HOSTS = [
    'mxtoday.online',
    'www.mxtoday.online',
    '*.railway.app',
    'localhost',
]


SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CAMBIAR-EN-PRODUCCION')


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

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


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


CSRF_TRUSTED_ORIGINS = [
    'https://mxtoday.online',
    'https://www.mxtoday.online',
]


SECURE_HSTS_SECONDS = 31536000 
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

print("✓ Configuración de producción cargada correctamente")
