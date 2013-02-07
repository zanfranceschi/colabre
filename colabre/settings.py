import os
from socket import gethostname

# Custom apps location
# PROJECT_ROOT = os.path.dirname(__file__)
# sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)).replace('colabre', 'colabre_web').replace('\\', '/')

def abs_path(_dir, forwardslash=True):
	result = os.path.join(_PROJECT_DIR, _dir)
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
	#'gadjo.requestprovider.middleware.RequestProvider',
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
	'colabre_openauth',
	'social_auth',
	#'south',
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


import urllib2
HTTP_PROXY = 'http://xxxxx:xxx'
proxy = urllib2.ProxyHandler({'http': HTTP_PROXY, 'https' : HTTP_PROXY})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)

AUTHENTICATION_BACKENDS = (
	#'emailusernames.backends.EmailAuthBackend',
	'django.contrib.auth.backends.ModelBackend',
	# add the social_auth authentication backend. We're not using the default
	# ModelBackend, but if you are, leave it in the list.
	'social_auth.backends.contrib.linkedin.LinkedinBackend',
)

# These settings are used by the social_auth app.
LINKEDIN_CONSUMER_KEY = 'xxxxxxx' # linkedin calls this the "API Key"
LINKEDIN_CONSUMER_SECRET = 'xxxxxx' # "Secret Key"
# Scope determines what linkedin permissions your app will request when users
# sign up. Linkedin reccomends requesting three.
LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress', 'r_fullprofile']
# Field selectors determine what data social_auth will get from linkedin
LINKEDIN_EXTRA_FIELD_SELECTORS = [
	'id',
	'email-address',
	'headline',
	'industry',
	'location',
	#'summary',
	#'specialties',
	#'positions',
	#'educations',
	#'skills',
	#'summary',
]
# extra_data determines what data will be stored in a JSON field in the
# UserSocialAuth table. This should parallel the field selectors.
LINKEDIN_EXTRA_DATA = [('id', 'id'),
						('first-name', 'first_name'),
						('last-name', 'last_name'),] + [
							(field, field.replace('-', '_'), True)
							for field in LINKEDIN_EXTRA_FIELD_SELECTORS
						]

# See the social_auth docs for all the configuration options
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/oauth/talent/new/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = SOCIAL_AUTH_NEW_USER_REDIRECT_URL

#LOGIN_ERROR_URL = '/oauth/error/'
#LOGIN_URL = "/oauth/login/"
#LOGIN_REDIRECT_URL = '/meu-perfil'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/meu-perfil/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/new-error-url/'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
	'colabre_openauth.pipeline.bind_to_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
	'social_auth.backends.pipeline.misc.save_status_to_session',
)

