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
	"""
	queryset_segments_jobs = Segment.objects.filter(jobtitle__job__active=True, jobtitle__job__approved=True).annotate(quantidade=Count('jobtitle__job')).order_by('-quantidade')
	queryset_segments_jobs = queryset_segments_jobs[0:5]
	ds_segments_jobs = DataPool(
       series=
        [{
		'options': { 'source': queryset_segments_jobs },
		'terms': {'name' : 'name', u'Número de Vagas' : 'quantidade'}
		}]
	)
	chart_segments_jobs = Chart(
        datasource = ds_segments_jobs, 
        series_options = 
          [{'options':{
              'type': 'bar',
              'stacking': False
              },
            'terms':{
              'name': [ u'Número de Vagas'], 
              }}],
        chart_options = {
			'chart' : 
			{
				'backgroundColor' : 'rgba(255, 255, 255, 0.0)',
			},
			'title': 
			{
				'text': ' '
			},
           	'xAxis': 
			 {
			 	'title': 
			 	{
					'text': ' ',
				}
			},
			'plotOptions' : 
			{ 
				'series' : 
				{
                    'dataLabels': 
					 {
                        'enabled': True,
                    },
                    'showInLegend': False,
                    'color' : 'rgba(70, 114, 193, 0.8)'
				}
			}
		}
	)
	
	queryset_segments_resumes = Segment.objects.filter().annotate(quantidade=Count('resume')).order_by('-quantidade')
	queryset_segments_resumes = queryset_segments_resumes[0:5]
	ds_segments_resumes = DataPool(
       series=
        [{
		'options': { 'source': queryset_segments_resumes },
		'terms': {'name' : 'name', u'Número de Vagas' : 'quantidade'}
		}]
	)
	chart_segments_resumes = Chart(
        datasource = ds_segments_resumes, 
        series_options = 
          [{'options':{
              'type': 'bar',
              'stacking': False
              },
            'terms':{
              'name': [ u'Número de Vagas'], 
              }}],
        chart_options = {
			'chart' : 
			{
				'backgroundColor' : 'rgba(255, 255, 255, 0.0)',
			},
			'title': 
			{
				'text': ' '
			},
           	'xAxis': 
			 {
			 	'title': 
			 	{
					'text': ' ',
				}
			},
			'plotOptions' : 
			{ 
				'series' :
				{
					'dataLabels' :
					{
						'enabled' : True
					},
					'showInLegend': False,
					'color' : 'rgba(70, 114, 193, 0.8)'
				},
			}
		}
	)
	"""
	return render(request, get_template_path("index.html"), { 'charts' : '[chart_segments_jobs,chart_segments_resumes]' })

def legal(request):
	return render(request, get_template_path("legal.html"))