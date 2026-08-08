"""
Django settings for config project.

Generated for ObsidianRPG — Tema #2 (Base del proyecto Django).

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rLyj_$-@du4H%yTNDQh+FCKJq_@-=hdj$kWzjO3IqvBBZ!wAyZ'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'huey.contrib.djhuey',
    'core',
    'orchestrator',
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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/models/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Media (audios uploaded through the orchestrator)
# https://docs.djangoproject.com/en/5.1/topics/files/

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Uploads: a 2-3 hour tabletop session audio (WAV 16kHz mono) weighs ~300-350 MB.
# FILE_UPLOAD_MAX_MEMORY_SIZE is the threshold above which Django already streams to disk
# instead of memory (not a size limit); DATA_UPLOAD_MAX_MEMORY_SIZE can reject the request if
# left at the 2.5 MB default, so it's raised explicitly.
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 1024  # 1 GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB


# Orchestrator: where campaign vaults live by default. Single local user (Oscar), whose
# Documentos folder was redirected off C: to a secondary disk — override via env var so a
# different machine (or a future user) isn't stuck with this one's drive letter.
DEFAULT_VAULT_BASE_DIR = os.environ.get(
    'VAULT_BASE_DIR', r'E:\Users\oscar\OneDrive\Documentos'
)


# Huey (background processing) — see decision log 2026-08-07 in docs/meta/contexto-para-ia.md:
# SQLite instead of Celery/Redis, single local user. Requires a second process running
# (`make huey`) besides `make run` — without it, jobs stay queued but never get processed.
HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'name': 'orchestrator',
    'filename': str(BASE_DIR / 'huey.sqlite3'),
    'immediate': False,
}
