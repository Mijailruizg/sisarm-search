from pathlib import Path

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

# === AUTENTICACIÓN Y REDIRECCIONES ===
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/inicio/'
              # Redirección si no está autenticado

# === AUTO FIELD POR DEFECTO PARA MODELOS ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
