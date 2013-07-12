from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.contrib import admin
import social_auth

admin.autodiscover()

urlpatterns = patterns('colabre_web.views',

	
	url(r'^admin-vagas/', include('colabre_web.views.admin_jobs')),
	
	
	#url(r'^test/(.+)/$', 'test.test', name='test'),
	
	url(r'^auxiliares/', include('colabre_web.views.generic')),
	
	url(r'^colabre-admin/', include('colabre_web.views.admin')),
	
	url(r'^inicio/', include('colabre_web.views.home')),
	
	url(r'^login/$', 'auth.login_', name='login'),
	url(r'^autenticar/$', 'auth.authenticate_', name='authenticate'),
	url(r'^logout/$', 'auth.logout_', name='logout'),
	
	url(r'^meu-perfil/', include('colabre_web.views.my_profile')),
	url(r'^minhas-vagas/', include('colabre_web.views.my_jobs')),
	
	url(r'^meu-curriculo/', include('colabre_web.views.my_resume')),
	
	url(r'^cadastro/$', 'registration.index', name='registration_index'),
	
	url(r'^vagas/', include('colabre_web.views.jobs')),
	url(r'^curriculos/', include('colabre_web.views.resumes')),
	
	url(r'^contato/', include('colabre_web.views.contact')),
	
	url(r'^$', 'home.index', name='home_index'),
	url(r'^legal/$', 'home.legal', name='home_legal'),
	
	url(r'^admin/', include(admin.site.urls)),
	
	url(r'', include('social_auth.urls')),
	#url(r'^oauth/', include('colabre_openauth.views')),
)