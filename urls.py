#file not used...
from django.conf.urls.defaults import *
from app.api import EntryResource
from django.contrib import admin

admin.autodiscover()

entry_resource = EntryResource()

urlpatterns = patterns('',
	(r'.', include('app.urls')),
	(r'', include('app.urls'))
)