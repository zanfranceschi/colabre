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
from django.db import connections
from colabre_web.models import *
from colabre_web.aux_models import *
from colabre_web.forms import *
from colabre_web.statistics.models import *
from django.conf.urls import patterns, url
import logging

logger = logging.getLogger('app')


urlpatterns = patterns('colabre_web.views.jobs',
	url(r'^$', 'index', name='jobs_index'),
	url(r'^parcial/buscar/$', 'partial_html_search', name='jobs_partial_html_search'),
	url(r'^parcial/detalhar/visualizacoes/(\d+)/$', 'partial_details_viewscount', name='jobs_partial_details_viewscount'),
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='jobs_partial_details'),
	url(r'^detalhar/(\d+)/$', 'detail', name='jobs_detail'),
)

def get_template_path(template):
	return 'jobs/%s' % template


def partial_details_viewscount(request, id):
	try:
		cursor = connections['stats'].cursor()
		cursor.execute("""select sum(count) total from 
							(
								select 
									1 as count, 
									session_key,
									access_date
								from colabre_web_jobstatistics 
								where job_id = %s 
								group by session_key, access_date
							) t""", [id])
		row = cursor.fetchone()
		response = HttpResponse(row[0] or 0)
		response['job-id'] = id
		return response
	except:
		logger.exception("-- colabre_web/views/jobs.py, partial_details_viewscount --")
		return HttpResponse('0')

def partial_details(request, id, search_term=None):
	job = Job.objects.get(id=id)
	response = render(request, get_template_path("partial/details.html"), { 'job' : job })
	response['job-id'] = id
	return response


def detail(request, id):
	job = Job.objects.get(id=id)
	return render(request, get_template_path("detail.html"), { 'job' : job })


def partial_html_search(request):
	if request.method == 'POST':
		job_titles = request.POST['job_titles']
		cities = request.POST['cities']
		term = request.POST['term']
		days = request.POST['days']
		page = request.POST['page']
		
		job_titles_ids = None
		if job_titles:
			job_titles_ids = [int(n) for n in job_titles.split("-")]
		
		cities_ids = None
		if cities:
			cities_ids = [int(n) for n in cities.split("-")]
		
		jobs, is_last_page, total_jobs = Job.view_search_public(term, job_titles_ids, cities_ids, int(days), page, 30)
		return render(request, get_template_path("partial/jobs.html"), {'total_jobs' : total_jobs, 'jobs' : jobs, 'is_last_page': is_last_page, 'q' : term, 'page' : page})
	else:
		return HttpResponse('')

def index(request):
	segments = Job.get_segments_for_search_filter()
	countries = Job.get_countries_for_search_filter()
	days = [15, 30, 60, 90, 120, 150]
	return render(request, get_template_path('index.html'), { 'countries' : countries, 'days' : days, 'segments' :  segments })
