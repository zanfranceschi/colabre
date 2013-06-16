from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import *
from colabre_web.models import *
import time
from colabre_web.forms import *
from helpers import *
from django.conf.urls import patterns, url
from chartit import *
from django.db.models import *

urlpatterns = patterns('colabre_web.views.home',
	#url(r'^parcial/alguma-chamada-ajax/$', 'partial_some_ajax_call', name='home_partial_some_ajax_call'),
)

def get_template_path(template):
	#return template
	return 'home/%s' % template

def index(request):
	#messages.info(request, 'Vaga criada.')
	#messages.success(request, 'Vaga criada.')
	#messages.error(request, 'Vaga criada.')
	#messages.warning(request, 'Vaga criada.')
	
	queryset = Segment.objects.filter(jobtitle__job__active=True, jobtitle__job__approved=True).annotate(quantidade=Count('jobtitle__job')).order_by('-quantidade')
	queryset = queryset[0:6]
	ds = DataPool(
       series=
        [{
		'options': { 'source': queryset },
		'terms': [ 'name', 'quantidade' ]
		}]
	)
	chart = Chart(
        datasource = ds, 
        series_options = 
          [{'options':{
              'type': 'column',
              'stacking': False},
            'terms':{
              'name': ['quantidade', ]
              }}],
        chart_options = 
          {'title': {
               'text': 'Weather Data of Boston and Houston'},
           'xAxis': {
                'title': {
                   'text': 'Month number'}}})
	
	return render(request, get_template_path("index.html"), { 'chart' : chart })

def legal(request):
	return render(request, get_template_path("legal.html"))