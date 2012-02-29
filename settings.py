# Colabre
from socket import gethostname

HOST = gethostname()

# alwaysdata
if HOST == 'http7' or HOST == 'ssh':
	DATABASES = {
		'default': {
			'ENGINE': 'django_mongodb_engine', 	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': 'zanfranceschi_colabre',                 	# Or path to database file if using sqlite3.
			'USER': '',                      	# Not used with sqlite3.
			'PASSWORD': '',                  	# Not used with sqlite3.
			'HOST': '',                      	# Set to empty string for localhost. Not used with sqlite3.
			'PORT': 27017,                      # Set to empty string for default. Not used with sqlite3.
		}
	}
	STATIC_ROOT = '/home/zanfranceschi/zanfranceschi/interface/static'
	STATICFILES_DIRS = ('/home/zanfranceschi/zanfranceschi/interface/static',)
	TEMPLATE_DIRS = ('/home/zanfranceschi/zanfranceschi/interface/templates',)
# localhost
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django_mongodb_engine', 	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': 'colabre',                 	# Or path to database file if using sqlite3.
			'USER': '',                      	# Not used with sqlite3.
			'PASSWORD': '',                  	# Not used with sqlite3.
			'HOST': '',                      	# Set to empty string for localhost. Not used with sqlite3.
			'PORT': 27017,                      # Set to empty string for default. Not used with sqlite3.
		}
	}
	STATIC_ROOT = 'D:\Projects\Colabre\svn\trunk\interface\static'
	STATICFILES_DIRS = ('D:/Projects/Colabre/svn/trunk/interface/static',)
	TEMPLATE_DIRS = ('D:/Projects/Colabre/svn/trunk/interface/templates',)


ADMINS = (
		# ('Your Name', 'your_email@example.com'),
)
DEBUG = True
TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS
ADMIN_MEDIA_PREFIX = '/static/admin/'
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_URL = '/static/'
TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'en-us'
FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'
SITE_ID = "4f4b8e23122da19aca7d58b2"
USE_I18N = True
USE_L10N = True
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
SECRET_KEY = '7+406+nmp@#6+civ58b7@ieo#c74*@=q&%^7qvt()_j38(^iif'
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
ROOT_URLCONF = 'main.urls'
MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
)
INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	#'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'djangotoolbox',
	'main',
	'tastypie',
	'django.contrib.admin',
	'django_mongodb_engine'
)
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
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
