"""
Configuración principal (Settings) para el backend del Sistema de Reservas.
Implementa validaciones de entorno para asegurar transiciones seguras
entre el desarrollo local y el despliegue en producción.
"""

import os
from pathlib import Path
from datetime import timedelta

# ==========================================
# 1. RUTAS BASE
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 2. SEGURIDAD Y ENTORNO
# ==========================================
# ADVERTENCIA: En producción, estas variables deben inyectarse desde el servidor (ej. archivo .env)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-=*_us3-c!tc=0@$+hmyvz3#-%xel@-y3h5e127hn2w_bih!@ea')

# Si la variable de entorno DJANGO_DEBUG es 'False', desactiva el modo de depuración
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Configuración dinámica de hosts permitidos
# Ej. export DJANGO_ALLOWED_HOSTS="api.midominio.com,127.0.0.1"
allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = allowed_hosts_env.split(',')

# ==========================================
# 3. APLICACIONES INSTALADAS
# ==========================================
DJANGO_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'channels',
]

LOCAL_APPS = [
    'api',
    'reservas',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==========================================
# 4. MIDDLEWARE
# ==========================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

# ==========================================
# 5. MOTORES DE PLANTILLAS Y ASGI/WSGI
# ==========================================
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

WSGI_APPLICATION = 'api.wsgi.application'
ASGI_APPLICATION = 'api.asgi.application'

# ==========================================
# 6. CONFIGURACIÓN DE CHANNELS (WEBSOCKETS)
# ==========================================
# Nota: Para escalar en producción, cambiar InMemoryChannelLayer por RedisChannelLayer
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# ==========================================
# 7. BASE DE DATOS
# ==========================================
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'sistemareservas'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', '12345678'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# ==========================================
# 8. AUTENTICACIÓN Y VALIDACIÓN DE CLAVES
# ==========================================
AUTH_USER_MODEL = 'reservas.Usuario'

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

# ==========================================
# 9. CONFIGURACIÓN DRF Y JWT (API REST)
# ==========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    
}

# ==========================================
# 10. CORS (Cross-Origin Resource Sharing)
# ==========================================
# Orígenes permitidos para interactuar con la API (Vue.js frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   
    "http://127.0.0.1:5173",
]

# ==========================================
# 11. INTERNACIONALIZACIÓN Y ZONA HORARIA
# ==========================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ==========================================
# 12. ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ==========================================
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')