import os

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).replace('colabre', 'colabre_web').replace('\\', '/')

def abs_path(_dir, forwardslash=True):
	result = os.path.join(_PROJECT_DIR, _dir)
	return result

DATABASE_ROUTERS = [
	'colabre_web.db_routers.StatisticsRouter',
]


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql', 	# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'colabre',                      # Or path to database file if using sqlite3.
		'USER': 'root',                      # Not used with sqlite3.
		'PASSWORD': 'root',                  # Not used with sqlite3.
		'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
	},
	'stats': {
		'ENGINE': 'django.db.backends.mysql', 	# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'colabre_stats',                      # Or path to database file if using sqlite3.
		'USER': 'root',                      # Not used with sqlite3.
		'PASSWORD': 'root',                  # Not used with sqlite3.
		'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
	}
}

STATIC_URL = '/static/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
HOST_ROOT_URL = 'http://127.0.0.1:8000'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'zzzz'
EMAIL_HOST_PASSWORD = 'zzzz'
EMAIL_PORT = 587
EMAIL_USE_TLS = True



EMAIL_FROM = 'no-reply@colabre.org'

USE_REAL_USER_NOTIFICATION = True

STATIC_ROOT = abs_path('static')

UPLOAD_DIR = abs_path('uploads').replace('_web', '')

FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'
AUTH_PROFILE_MODULE = 'colabre_web.UserProfile'
LOGIN_URL = '/login'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS
TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'pt-br'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''


STATICFILES_DIRS = (
	abs_path('public'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'hj266pj!n0d7&amp;_#lqtq=x@6c+g%5p118&amp;@f4@bhgalj-udfyr9'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'colabre_web.middlewares.ColabreMiddleware',
    'colabre_web.middlewares.StatisticsMiddleware',
    'colabre_web.middlewares.HandleErrorMiddleware',
	#'gadjo.requestprovider.middleware.RequestProvider',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_SAVE_EVERY_REQUEST = True

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages"
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'colabre_web.urls'

WSGI_APPLICATION = 'colabre.wsgi.application'

TEMPLATE_DIRS = (
	abs_path('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'colabre_web',
    'django.contrib.admin',
	'social_auth',
	'chartit',
)

SERIALIZATION_MODULES = {
	'json': 'wadofstuff.django.serializers.json'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'colabre_web_cache',
    }
}

import sys

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
		'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
	
	'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s  %(module)s %(message)s'
        },
    },
		
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
		'app' : {
			'handlers' : ['console'],
			'level' : 'DEBUG',
			'propagate' : True,
		}
    }
}

from colabre_web.oauth.settings import *