import urllib2
HTTP_PROXY = ''
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
    'social_auth.backends.twitter.TwitterBackend',
)

# These settings are used by the social_auth app.
LINKEDIN_CONSUMER_KEY = '' # linkedin calls this the "API Key"
LINKEDIN_CONSUMER_SECRET = '' # "Secret Key"
# Scope determines what linkedin permissions your app will request when users
# sign up. Linkedin reccomends requesting three.
LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress', 'r_fullprofile']
# Field selectors determine what data social_auth will get from linkedin
LINKEDIN_EXTRA_FIELD_SELECTORS = [
    'id',
    'email-address',
    'date-of-birth',
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

TWITTER_CONSUMER_KEY         = 'AXu7w1hJNFvRmv0zc6rUDQ'
TWITTER_CONSUMER_SECRET      = 'T6BzcKZZFLmBKOPRFGR1yFTgk3DP1CHc6ErJY2Azs'


# See the social_auth docs for all the configuration options
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/oauth/talent/new/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = SOCIAL_AUTH_NEW_USER_REDIRECT_URL



SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/meu-perfil/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/new-error-url/'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    #'colabre_openauth.pipeline.check_oauth_email_existence',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'colabre_openauth.pipeline.bind_to_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',
)

SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_URL = '/cadastro/linkedin/email-existente'