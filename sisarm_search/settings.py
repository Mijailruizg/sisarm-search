from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# === RUTAS Y SEGURIDAD ===
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-clave-temporal-para-desarrollo'
DEBUG = True
ALLOWED_HOSTS = []

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
            ],
        },
    },
]

WSGI_APPLICATION = 'sisarm_search.wsgi.application'

# === BASE DE DATOS ===
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
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

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
if DEBUG:
    EMAIL_DEBUG = True
    EMAIL_TIMEOUT = 20  # segundos

    # Por compatibilidad, en desarrollo se puede usar un backend que escriba
    # los correos a disco. Esto se hará SOLO si no se definió explícitamente
    # la variable de entorno `EMAIL_BACKEND` o si `USE_FILE_EMAIL` está a true.
    use_file_email = os.getenv('USE_FILE_EMAIL', 'True').lower() in ('1', 'true', 'yes')
    if use_file_email and 'EMAIL_BACKEND' not in os.environ:
        EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
