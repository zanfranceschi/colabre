# celery settings

from colabre.settings import INSTALLED_APPS 

INSTALLED_APPS += ('djcelery',)

from colabre_web.statistics.tasks import *

import djcelery

djcelery.setup_loader()