from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import *
from colabre_web.models import *
from django.db.models import Q
import time
from colabre_web.forms import *
from helpers import * 
from django.core import serializers
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.my_jobs',
	
	url(r'^$', 'index', name='my_jobs_index'),
	url(r'^criar/$', 'create', name='my_jobs_create'),
	url(r'^editar/([\d]+)/$', 'edit', name='my_jobs_edit'),
	url(r'^confirmar-exclusao/([\d]+)/$', 'confirm_del', name='my_jobs_confirm_del'),
	url(r'^excluir/([\d]+)/$', 'delete', name='my_jobs_delete'),
	
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='my_jobs_partial_details'),
	url(r'^parcial/buscar/$', 'partial_html_search'),
)

def get_template_path(template):
	return 'my-jobs/%s' % template

def _index_data(request):
	profile = request.user.get_profile()
	segments = UserProfile.get_segments_for_search_filter(profile)
	countries = UserProfile.get_countries_for_search_filter(profile)
	days = [3, 7, 15, 30, 60, 90, 120, 150]
	return { 'countries' : countries, 'days' : days, 'segments' :  segments }
	
@login_required
def index(request):
	context = _index_data(request)
	return render(request, get_template_path('index.html'), context)

@login_required
def partial_details(request, id, search_term=None):
	job = Job.objects.get(id=id)
	response = render(request, get_template_path("partial/details.html"), { 'job' : job })
	response['job-id'] = id
	return response

@login_required
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
		
		jobs, is_last_page, total_jobs = Job.view_search_my_jobs(request.user.get_profile(), term, job_titles_ids, cities_ids, int(days), page, 30)
		return render(request, get_template_path("partial/jobs.html"), {'total_jobs' : total_jobs, 'jobs' : jobs, 'is_last_page': is_last_page, 'q' : term, 'page' : page})
	else:
		return HttpResponse('')
	

@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def partial_toggle_published(request, job_id):
	job = Job.objects.get(id=job_id)
	job.published = not job.published
	job.save()
	return render(request, get_template_path('partial/job-item.html'), {'job' : job})


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def create(request):	
	template = None
	profile = request.user.get_profile()
	context = {}
	if request.method == 'POST':
		form = JobForm(request.POST, profile=profile)
		if form.is_valid():
			form.save()
			template = get_template_path('index.html')
			context = _index_data(request)
			messages.success(request, 'Vaga criada.')
		else:
			messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
			template = get_template_path('create.html')
	else:
		template = get_template_path('create.html')
		form = JobForm(profile=profile)
	context.update({'form' : form, 'action' : '/minhas-vagas/criar/'})
	return render(request, template, context)


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def edit(request, job_id):
	template = None
	profile=request.user.get_profile()
	job = Job.objects.get(id=job_id, profile=profile)
	context = {}
	if job.is_editable:
		if request.method == 'POST':
			form = JobForm(request.POST, job_id=job.id, profile=profile)
			if form.is_valid():
				form.save()
				template = get_template_path('index.html')
				context = _index_data(request)
				messages.success(request, 'Vaga atualizada.')
			else:
				template = get_template_path('edit.html')
				messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
		else:
			template = get_template_path('edit.html')
			form = JobForm(profile=profile, job_id=job.id)
		context.update({'form' : form, 'action' : '/minhas-vagas/editar/' + job_id + '/'})
		return render(request, template, context)
	else:
		messages.error(request, u'Esta vaga foi criada a mais de 24 horas atrás. As vagas só podem ser editadas até 24 após sua criação. Por favor, considere excluí-la e criar uma nova.')
		return HttpResponseRedirect(reverse('colabre_web.views.my_jobs.index'))

	
@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def confirm_del(request, job_id):
	try:	
		job = Job.objects.get(id=job_id)
		return render(request, get_template_path('confirm-del.html'), {'job' : job})
	except Job.DoesNotExist:
		return render(request, get_template_path('index.html'))


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def delete(request, job_id):
	context = {}
	try:
		job = Job.objects.get(id=job_id)
		job.delete()
		messages.success(request, u'Vaga excluída.')
		context = _index_data(request)
	except Job.DoesNotExist:
		pass
	return render(request, get_template_path('index.html'), context)
