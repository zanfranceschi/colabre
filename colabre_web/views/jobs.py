from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
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
from urlparse import urljoin
from colabre_web import services, utils

logger = logging.getLogger('app')


urlpatterns = patterns('colabre_web.views.jobs',
	url(r'^$', 'index', name='jobs_index'),
	url(r'^parcial/buscar/$', 'partial_html_search', name='jobs_partial_html_search'),
	url(r'^parcial/detalhar/visualizacoes/(\d+)/$', 'partial_details_viewscount', name='jobs_partial_details_viewscount'),
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='jobs_partial_details'),
	url(r'^detalhar/(\d+)/$', 'detail', name='jobs_detail'),
	
	
	url(r'^criar/$', 'create', name='jobs_create'),
	url(r'^validar-email/(\d+)/(.+)/$', 'validate_email', name='jobs_validate_email'),
    url(r'^excluir/(\d+)/(.+)/$', 'delete', name='jobs_delete'),
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

def partial_details(request, id, q=None):
	job = Job.objects.get(id=id)
	response = render(request, get_template_path("partial/details.html"), { 'job' : job, 'q' : q })
	response['job-id'] = id
	return response


def detail(request, id):
	job = Job.objects.get(id=id)
	return render(request, get_template_path("detail.html"), { 'job' : job })


def partial_html_search(request):
	if request.method == 'POST':
		term = request.POST['term']
		page = request.POST['page']
		jobs, is_last_page, total_jobs = Job.view_search_public(term, page, 30)
		return render(request, get_template_path("partial/jobs.html"), {'total_jobs' : total_jobs, 'jobs' : jobs, 'is_last_page': is_last_page, 'q' : term, 'page' : page})
	else:
		return HttpResponse('')

def index(request):
	initial_query = ''
	if ('q' in request.GET):
		initial_query = request.GET['q']
	return render(request, get_template_path('index.html'), { 'initial_query' : initial_query })

def create(request):
	template = None
	profile = None
	if (not request.user.is_anonymous()):
		profile = request.user.get_profile()

	context = {}
	if request.method == 'POST':
		form = JobForm(request.POST, profile=profile, ip=utils.get_client_ip(request))
		if form.is_valid():
			created_job = form.save()
			template = get_template_path('index.html')
			if (not created_job.admin_approved):
				messages.success(request, 
					u'Sua vaga foi submetida para aprovação.')
			else:
				messages.success(request, 
					u'Sua vaga foi criada e publicada com sucesso.')

			if (profile is not None):
				return redirect(reverse('colabre_web.views.my_jobs.index'))
			else:
				return redirect(reverse('colabre_web.views.jobs.create'))
		else:
			messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
			template = get_template_path('create.html')
	else:
		template = get_template_path('create.html')
		form = JobForm(profile=profile)
	context.update({'form' : form, 'action' : reverse('colabre_web.views.jobs.create')})
	return render(request, template, context)


def validate_email(request, id, email):
	if (request.method != 'POST'):
		try:
			job = Job.objects.get(id=id, contact_email=email, contact_email_verified=False)
			form = ValidateJobForm()
			return render(request, get_template_path('validate-email.html'), { 'form' : form, 'action' : reverse('colabre_web.views.jobs.validate_email', args=(id, email)) })
		except Job.DoesNotExist:
			return HttpResponseRedirect(reverse('colabre_web.views.home.index'))
	elif (request.method == 'POST'):
		form = ValidateJobForm(request.POST)
		if (form.is_valid()):
			uuid = request.POST['uuid']
			try:
				services.jobs.validate_email(id, email, uuid)
				messages.success(request, u"Email validado! Sua vaga está publicada agora.")
				job = Job.objects.get(pk=id)
				return render(request, get_template_path('detail.html'), { 'job' : job })
			except Job.DoesNotExist:
				messages.error(request, u"Não encontramos uma vaga com o código informado. Tente novamente, por favor.")
				return render(request, get_template_path('validate-email.html'), { 'form' : ValidateJobForm(), 'action' : reverse('colabre_web.views.jobs.validate_email', args=(id, email)) })
		else:
			return render(request, get_template_path('validate-email.html'), { 'form' : form, 'action' : reverse('colabre_web.views.jobs.validate_email', args=(id, email)) })			
		

def delete(request, id, email):
	if (request.method != 'POST'):
		try:
			job = Job.objects.get(id=id, contact_email=email, active=True)
			form = ValidateJobForm()
			return render(request, get_template_path('delete.html'), { 'job' : job, 'form' : form, 'action' : reverse('colabre_web.views.jobs.delete', args=(id, email)) })
		except Job.DoesNotExist:
			return redirect(reverse('colabre_web.views.home.index'))
	elif (request.method == 'POST'):
		form = ValidateJobForm(request.POST)
		if (form.is_valid()):
			uuid = request.POST['uuid']
			try:
				job = Job.objects.get(id=id, contact_email=email, uuid=uuid).delete()
				messages.success(request, u"Sua vaga foi excluída do Colabre.")
				return redirect(reverse('colabre_web.views.home.index'))
			except Job.DoesNotExist:
				job = Job.objects.get(id=id, contact_email=email, active=True)
				messages.error(request, u"Código inválido. Tente novamente, por favor.")
				return render(request, get_template_path('delete.html'), { 'job' : job, 'form' : ValidateJobForm(), 'action' : reverse('colabre_web.views.jobs.delete', args=(id, email)) })
		else:
			return render(request, get_template_path('delete.html'), { 'form' : form, 'action' : reverse('colabre_web.views.jobs.delete', args=(id, email)) })

