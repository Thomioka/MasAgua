import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'masagua.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'masagua.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ROLES = (
    ('cliente', 'Cliente'),
    ('administrador', 'Administrador'),
)

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'  # o donde quieras redirigir al iniciar sesión
LOGOUT_REDIRECT_URL = '/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TRANSBANK_CONFIG = {
    'WEBPAY_COMMERCE_CODE': '597055555532',  # Código de comercio TEST
    'WEBPAY_API_KEY': '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',  # API Key TEST
    'WEBPAY_ENVIRONMENT': 'TEST',  # Ambiente de pruebas
    'WEBPAY_RETURN_URL': 'https://5ede-2803-c600-d10f-e34c-b9ef-f850-bc6f-4bd0.ngrok-free.app/webpay/commit',  # Reemplaza con tu URL de ngrok
}