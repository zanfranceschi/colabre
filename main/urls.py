from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('main.views',
	url(r'^x/$', 'x'),
	url(r'^$', 'index'),
	url(r'^login/$', 'login_view'),
	url(r'^logout/$', 'logout_view'),
	url(r'^autenticar/$', 'autenticar'),
	url(r'^registrar/$', 'register'),
	url(r'^registrar/submeter/$', 'register_submit'),
	url(r'^empresas/$', 'empresas'),
	url(r'^empresa/([\d\w]+)/$', 'empresa'),
	url(r'^vagas/busca/resultado/$', 'vagas_busca_resultado'),
	url(r'^vagas/busca/$', 'vagas_busca'),
	url(r'^vagas/$', 'vagas'),
	url(r'^vaga/(\d+)/$', 'vaga'),
	url(r'^tag/([\w\s\d]+)/$', 'tag'),
	url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('main.aux_views',
	url(r'^vagas/titulos/sugestoes/$', 'job_titles_suggestion'),
	url(r'^cidades/(\w{2})/$', 'cities_by_state'),
	url(r'^cidades/sugestoes/$', 'cities_suggestion'),
	url(r'^estados/$', 'states'),
	url(r'^usuario/$', 'search_username'),
	
)