import os
import sys
from socket import gethostname

# Custom apps location
# PROJECT_ROOT = os.path.dirname(__file__)
# sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).replace('colabre', 'colabre_web').replace('\\', '/')

def abs_path(dir, forwardslash=True):
	result = os.path.join(_PROJECT_DIR, dir)
	return result

HOST = gethostname()

if HOST != 'http7' and HOST != 'ssh': # localhost
	DATABASES = {
		'backup': {
			'ENGINE': 'django.db.backends.sqlite3', 	# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': 'colabre.db',                      # Or path to database file if using sqlite3.
			'USER': 'root',                      # Not used with sqlite3.
			'PASSWORD': 'root',                  # Not used with sqlite3.
			'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
			'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
		},
		'default': {
			'ENGINE': 'django.db.backends.mysql', 	# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': 'colabre',                      # Or path to database file if using sqlite3.
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

else: #alwaysdata
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3', 			# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': ' /home/zanfranceschi/www/colabre.db',      # Or path to database file if using sqlite3.
			'USER': '',                      # Not used with sqlite3.
			'PASSWORD': '',                  # Not used with sqlite3.
			'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
			'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
		}
	}
	
	STATIC_URL = '/'
	HOST_ROOT_URL = 'http://www.colabre.org'

EMAIL_FROM = 'no-reply@colabre.org'

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

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
	'south',
)

'''
SERIALIZATION_MODULES = {
	'json': 'wadofstuff.django.serializers.json'
}
'''

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'colabre_web_cache',
    }
}

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
