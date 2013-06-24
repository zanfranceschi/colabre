from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf.urls import patterns, url
import logging
from colabre_web.services import jobs
from django.contrib.auth.decorators import login_required, user_passes_test
import traceback


logger = logging.getLogger('app')

urlpatterns = patterns('colabre_web.views.admin',
	url(r'^vaga/aprovar/(\d+)/(.+)$', 'job_approve', name='admin_job_approve'),
)

def get_template_path(template):
	return 'jobs/%s' % template

@login_required
def job_approve(request, id, uuid):
	try:
		jobs.admin_approve(id, uuid)
		messages.success(request, u"Vaga aprovada")
	except Exception, ex:
		messages.error(request, ex.message)
		messages.error(request, traceback.format_exc())
	
	return render(request, "admin/index.html")
	