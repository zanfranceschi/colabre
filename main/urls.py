from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('main.views',
	url(r'^$', 'index'),
	url(r'^empresas/$', 'empresas'),
	url(r'^empresa/([\d\w]+)/$', 'empresa'),
	url(r'^vagas/busca/resultado/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/(.+)/$', 'vagas_busca_resultado'),
	url(r'^vagas/busca/$', 'vagas_busca'),
	url(r'^vagas/$', 'vagas'),
	url(r'^vaga/(\d+)/$', 'vaga'),
	url(r'^tag/([\w\s\d]+)/$', 'tag'),
	url(r'^admin/', include(admin.site.urls)),

)
