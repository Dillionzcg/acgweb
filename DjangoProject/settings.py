"""
Django settings for DjangoProject project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!l(cj!#z@c&q7!u9mj*r1a=_uhklshlwxm&=)dy!#3)9jf_-76'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
<<<<<<< HEAD
    'daphne',
    'chat',
=======
>>>>>>> 4d04697ac3bdaf0b50168b1a496a436f7cff8b65
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
    'channels',
=======
>>>>>>> 4d04697ac3bdaf0b50168b1a496a436f7cff8b65
    'acg_core',
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

ROOT_URLCONF = 'DjangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'DjangoProject.wsgi.application'
<<<<<<< HEAD
ASGI_APPLICATION = 'DjangoProject.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
=======
>>>>>>> 4d04697ac3bdaf0b50168b1a496a436f7cff8b65

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- 修改重点：语言与时区 ---
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
DEEPSEEK_API_KEY = "sk-e9d4ab9b51d24a0486baef6928eb7d5f"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 认证配置 ---
AUTH_USER_MODEL = 'acg_core.User'
AUTHENTICATION_BACKENDS = [
    'acg_core.backends.MultiLoginBackend',
    'django.contrib.auth.backends.ModelBackend',
]
<<<<<<< HEAD
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

=======
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
>>>>>>> 4d04697ac3bdaf0b50168b1a496a436f7cff8b65
