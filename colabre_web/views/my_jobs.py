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
	
	url(r'^parcial/buscar/([\d]+)/(.+)/$', 'partial_html_search'),
	url(r'^parcial/buscar/(.+)/$', 'partial_html_search'),
	url(r'^parcial/buscar/$', 'partial_html_search'),
	#url(r'^parcial/alternar-ativacao/([\d]+)/$', 'partial_toggle_published'),
	
	url(r'^parcial/buscar-cargo/(.+)/$', 'partial_json_search_job_title', name= 'my_jobs_partial_json_search_job_title'),
	url(r'^parcial/buscar-segmento/(.+)/$', 'partial_json_search_segment', name= 'my_jobs_partial_json_search_segment'),
	url(r'^parcial/buscar-cidade/(.+)/$', 'partial_json_search_city', name= 'my_jobs_partial_json_search_city'),
	url(r'^parcial/buscar-empresa/(.+)/$', 'partial_json_search_company', name= 'my_jobs_partial_json_search_company'),
)

def get_template_path(template):
	return 'my-jobs/%s' % template

@login_required
@handle_exception
def index(request):
	return render(request, get_template_path('index.html'))


@login_required
@handle_exception
def partial_html_search(request, before_id=0, q=None):
	jobs, exists = Job.view_search_my_jobs(request.user.get_profile(), before_id, q, 100)
	return render(request, get_template_path("partial/jobs.html"), {'jobs' : jobs, 'exists': exists, 'q' : q})

@login_required
@handle_exception
def partial_json_search_job_title(request, q):
	list = serializers.serialize("json", JobTitle.objects.filter(name__icontains=q).order_by("name")[:10])
	return HttpResponse(list, mimetype="application/json")

@login_required
@handle_exception
def partial_json_search_segment(request, q):
	list = serializers.serialize("json", Segment.objects.filter(name__icontains=q).order_by("name")[:10])
	return HttpResponse(list, mimetype="application/json")

@login_required
@handle_exception
def partial_json_search_city(request, q):
	list = serializers.serialize("json", PoliticalLocation.objects.filter(city_name__istartswith=q).order_by("city_name")[:50], extras=('name',))
	return HttpResponse(list, mimetype="application/json")
	
@login_required
@handle_exception
def partial_json_search_company(request, q):
	list = serializers.serialize("json", Company.objects.filter(name__icontains=q).order_by("name")[:10])
	return HttpResponse(list, mimetype="application/json")
	
@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def partial_toggle_published(request, job_id):
	job = Job.objects.get(id=job_id)
	job.published = not job.published
	job.save()
	return render(request, get_template_path('partial/job-item.html'), {'job' : job})


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def create(request):	
	template = None
	profile = request.user.get_profile()
	if request.method == 'POST':
		form = JobForm(request.POST, profile=profile)
		if form.is_valid():
			form.save()
			template = get_template_path('index.html')
			messages.success(request, 'Vaga criada.')
		else:
			messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
			template = get_template_path('create.html')
	else:
		template = get_template_path('create.html')
		form = JobForm(profile=profile)
	return render(request, template, {'form' : form, 'action' : '/minhas-vagas/criar/'})


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def edit(request, job_id):
	template = None
	profile=request.user.get_profile()
	job = Job.objects.get(id=job_id)
	if job.is_editable:
		if request.method == 'POST':
			form = JobForm(request.POST, instance=job, profile=profile)
			if form.is_valid():
				form.save()
				template = get_template_path('index.html')
				messages.success(request, 'Vaga atualizada.')
			else:
				template = get_template_path('edit.html')
				messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
		else:
			template = get_template_path('edit.html')
			form = JobForm(profile=profile, instance=job)
		return render(request, template, {'form' : form, 'action' : '/minhas-vagas/editar/' + job_id + '/'})
	else:
		messages.error(request, u'Esta vaga foi criada a mais de 24 horas atrás. As vagas só podem ser editadas até 24 após sua criação. Por favor, considere excluí-la e criar uma nova.')
		return HttpResponseRedirect(reverse('colabre_web.views.my_jobs.index'))

	
@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def confirm_del(request, job_id):
	try:	
		job = Job.objects.get(id=job_id)
		return render(request, get_template_path('confirm-del.html'), {'job' : job})
	except Job.DoesNotExist:
		return render(request, get_template_path('index.html'))


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def delete(request, job_id):
	try:
		job = Job.objects.get(id=job_id)
		job.delete()
		messages.success(request, u'Vaga excluída.')
		return render(request, get_template_path('index.html'))
	except Job.DoesNotExist:
		return render(request, get_template_path('index.html'))
