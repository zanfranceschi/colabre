from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from datetime import *

from colabre_web.models import *
from colabre_web.aux_models import *
from colabre_web.forms import *
#from colabre_web.statistics.models import *

import time
from helpers import *
from django.core import serializers
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.resumes',
	url(r'^$', 'index', name='resumes_index'),
	url(r'^parcial/buscar/$', 'partial_html_search'),
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='resumes_partial_details'),
	url(r'^visualizar/(\d+)/$', 'detail', name='resumes_detail'),
)

def get_template_path(template):
	return 'resumes/%s' % template


def partial_details(request, id, search_term = None):
	resume = Resume.objects.get(id=id)
	#log_resume_request(request, search_term, resume)
	response = render(request, get_template_path("partial/details.html"), { 'resume' : resume })
	response['resume-id'] = id
	return response
	

def detail(request, id):
	resume = Resume.objects.get(id=id)
	return render(request, get_template_path("detail.html"), { 'resume' : resume })


def partial_html_search(request):
	if request.method == 'POST':
		segments = request.POST['segments']
		cities = request.POST['cities']
		term = request.POST['term']
		page = request.POST['page']
		
		segment_ids = None
		if segments:
			segment_ids = [int(n) for n in segments.split("-")]
		
		cities_ids = None
		if cities:
			cities_ids = [int(n) for n in cities.split("-")]
		
		resumes, is_last_page, total_resumes = Resume.view_search_public(term, segment_ids, cities_ids, page, 30)
		return render(request, get_template_path("partial/resumes.html"), {'total_resumes' : total_resumes, 'resumes' : resumes, 'is_last_page': is_last_page, 'q' : term, 'page' : page})
	else:
		return HttpResponse('')


def index(request):
	segments = Resume.get_segments_for_search_filter()
	countries = Resume.get_countries_for_search_filter()
	return render(request, get_template_path('index.html'), { 'countries' : countries, 'segments' :  segments })
