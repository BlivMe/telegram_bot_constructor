from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com']  # тут указать реальный домен

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'db_name'),
        'USER': os.getenv('POSTGRES_USER', 'db_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'db_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# КОРРЕКТНЫЕ настройки CORS для продакшена
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",  # Указать реальный адрес фронтенда
]