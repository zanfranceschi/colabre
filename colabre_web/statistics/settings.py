# celery settings

from colabre.settings import INSTALLED_APPS 

INSTALLED_APPS += ('djcelery',)

from colabre_web.statistics.tasks import *

import djcelery

djcelery.setup_loader()

GEOIP_DATAFILE_PATH = 'C:/Users/zanfranceschi/Projects/Colabre/svn/data/GeoLiteCity.dat'

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017