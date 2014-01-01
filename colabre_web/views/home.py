from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf.urls import patterns


urlpatterns = patterns('colabre_web.views.home',
	#url(r'^parcial/alguma-chamada-ajax/$', 'partial_some_ajax_call', name='home_partial_some_ajax_call'),
)

def get_template_path(template):
	return 'home/%s' % template

def index(request):
	return render(request, get_template_path("index.html"))
	#return HttpResponseRedirect(reverse('colabre_web.views.jobs.index'))

def about(request):
	return render(request, get_template_path("about.html"))

def legal(request):
	return render(request, get_template_path("legal.html"))