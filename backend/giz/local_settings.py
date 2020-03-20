import os
from .settings import *

SITE_NAME = 'GIZ DASHBOARD'

GIZ_APPS = [
    'dashboard',
] 
INSTALLED_APPS += GIZ_APPS
# AUTH_USER_MODEL = os.getenv('AUTH_USER_MODEL', 'users.Profile')

TEMP_DIR = os.path.join(BASE_DIR, '../frontend/templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMP_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # added by razinal
                'giz.context_processors.resource_urls',
            ],
        },
    },
]
# Static files(CSS, Javascript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, '../frontend/staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../frontend/static'),
]