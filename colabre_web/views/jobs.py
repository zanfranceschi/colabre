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
from colabre_web.statistics.models import *

import time
from helpers import handle_exception, log_request as view_log_request
from django.core import serializers
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.jobs',
	url(r'^$', 'index', name='jobs_index'),
	url(r'^parcial/buscar/$', 'partial_html_search'),
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='jobs_partial_details'),
	url(r'^visualizar/(\d+)/$', 'detail', name='jobs_detail'),
)

def get_template_path(template):
	return 'jobs/%s' % template

@view_log_request
@handle_exception
def partial_details(request, id, search_term = None):
	job = Job.objects.get(id=id)
	log_job_request(request, search_term, job)
	job_view_count = 10
	response = render(request, get_template_path("partial/details.html"), { 'job' : job, 'job_view_count' : job_view_count})
	response['job-id'] = id
	return response

@view_log_request
@handle_exception
def detail(request, id):
	job = Job.objects.get(id=id)
	return render(request, get_template_path("detail.html"), { 'job' : job })

@view_log_request
@handle_exception
def partial_html_search(request):
	if request.method == 'POST':
		job_titles = request.POST['job_titles']
		locations = request.POST['locations']
		term = request.POST['term']
		days = request.POST['days']
		page = request.POST['page']
		
		job_titles_ids = None
		if job_titles:
			job_titles_ids = [int(n) for n in job_titles.split("-")]
		
		locations_ids = None
		if locations:
			locations_ids = [int(n) for n in locations.split("-")]
		
		jobs, is_last_page, total_jobs = Job.view_search_public(term, job_titles_ids, locations_ids, int(days), page, 30)
		return render(request, get_template_path("partial/jobs.html"), {'total_jobs' : total_jobs, 'jobs' : jobs, 'is_last_page': is_last_page, 'q' : term, 'page' : page})
	else:
		return HttpResponse('')

@view_log_request
@handle_exception
def index(request):
	segments = Job.getSegmentsForSearchFilter()
	countries = Job.getCountriesForSearchFilter()
	days = [3, 7, 15, 30, 60, 90, 120, 150]
	return render(request, get_template_path('index.html'), { 'countries' : countries, 'days' : days, 'segments' :  segments })
