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

logger = logging.getLogger('app')


urlpatterns = patterns('colabre_web.views.jobs',
	url(r'^$', 'index', name='jobs_index'),
	url(r'^parcial/buscar/$', 'partial_html_search', name='jobs_partial_html_search'),
	url(r'^parcial/detalhar/visualizacoes/(\d+)/$', 'partial_details_viewscount', name='jobs_partial_details_viewscount'),
	url(r'^parcial/detalhar/(\d+)/(.*)/$', 'partial_details', name='jobs_partial_details'),
	url(r'^detalhar/(\d+)/$', 'detail', name='jobs_detail'),
	
	
	url(r'^criar/$', 'create', name='jobs_create'),
	url(r'^validar-email-vaga/(\d+)/(.+)/$', 'validate_job_email', name='jobs_validate_job_email'),
    url(r'^excluir/(.+)/$', 'delete', name='jobs_delete'),
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
	days = [30, 60, 90, 120, 150]
	return render(request, get_template_path('index.html'), { 'countries' : countries, 'days' : days, 'segments' :  segments })

















"""
	Criação de uma vaga pública
"""
def create(request):
	if (not request.user.is_anonymous()):
		return HttpResponseRedirect(reverse('colabre_web.views.home.index'))
		"""
			Usuários logados não postam vagas públicas
		"""
	else:
		if request.method != 'POST':
			"""
				1º Passo - mostrar formulário de cadastro
			"""
			form = JobForm(public=True)

		elif request.method == 'POST':
			"""
				2º Passo - registro submetido. Envia email para aprovação.
			"""
			form = JobForm(request.POST, public=True)
			if form.is_valid():
				created_job = form.save()
				send_mail(
						u"Colabre | Aprovação de Nova Vaga Pública",
						created_job.to_string(),
						colabre.settings.EMAIL_FROM, 
						[colabre.settings.EMAIL_CONTACT], 
						fail_silently=False)
				messages.success(request, 
								u'Sua vaga foi submetida para aprovação. '
								u'A aprovação não deve levar mais do que alguns minutos e, '
								u'assim que concluída, você receberá uma notificação por email.')
		else:
			messages.error(request, 'Por favor, verifique o preenchimento da vaga.')

		return render(request, get_template_path('create.html'), {'form' : form, 'action' : '/vagas/criar/'})


def validate_job_email(request, id, public_uuid):
	"""
		3º Passo - validar email da vaga
	"""
	try:
		job = Job.objects.get(id=id, public_uuid=public_uuid, email_validated=False)
		job.email_validated = True
		job.approved = True
		job.approval_date = datetime.now()
		job.save() # email validado
		
		message = u"""	<strong>{0}</strong>, sua vaga foi ativada. Se quiser excluí-la, acesse o 
					 	endereço <a href='{1}'>{1}</a>, e informe o código <strong>{2}</strong> e seu email. 
						Nós lhe enviamos um email com estas instruções para que 
						não precise anotá-las agora.""".format(
															job.contact_name, 
															urljoin(colabre.settings.HOST_ROOT_URL, reverse('colabre_web.views.jobs.delete', args=(job.public_uuid,))),
															job.public_uuid
														)
		messages.success(request, message)
		send_mail(
			u"Colabre | Informação de Vaga",
			u"""{0},

Sua vaga de {1} foi ativada. Se quiser excluí-la, acesse o endereço {2}{3}, e informe o código {4} e seu email.			
			
Abraços,

Equipe Colabre
www.colabre.org			
""".format(
		job.contact_name, 
		job.job_title, 
		colabre.settings.HOST_ROOT_URL,
		reverse('colabre_web.views.jobs.delete', args=(job.public_uuid,)),
		job.public_uuid
		),
			colabre.settings.EMAIL_FROM, 
			[job.contact_email], 
			fail_silently=False)
		return render(request, get_template_path("detail.html"), { 'job' : job })
	except Job.DoesNotExist:
		return HttpResponse("{0} / {1}".format(id, public_uuid))



"""
	Excluir vaga
"""
def delete(request, public_uuid):
	if (request.method != 'POST'):
		"""
			Informe o código e email...
		"""
		try:
			job = Job.objects.get(public_uuid=public_uuid)
			return render(request, get_template_path("delete.html"), { 'job' : job, 'form' : DeleteJobForm(), 'action' : reverse('colabre_web.views.jobs.delete', args=(public_uuid,)) })
		except Job.DoesNotExist:
			return HttpResponseRedirect(reverse('colabre_web.views.home.index'))
	elif (request.method == 'POST'):
		try:
			pass
		except Job.DoesNotExist:
			pass

