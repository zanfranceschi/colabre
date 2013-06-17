from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
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


urlpatterns = patterns('colabre_web.views.admin',
	url(r'^vaga/aprovar/(\d+)/(.+)$', 'job_approve', name='admin_job_approve'),
)

def get_template_path(template):
	return 'jobs/%s' % template


def job_approve(request, id, uuid):
	try:
		approved_job = Job.approve(id, uuid)
		if (approved_job is not None):
			user = approved_job.profile.user
			message = u"""{0},

Obrigado por usar o Colabre! Acabamos de aprovar a sua vaga para {1}.
Você pode vê-la em {3}vagas/detalhar/{2}

Abraços,

Equipe Colabre
www.colabre.org
""".format(user.first_name, approved_job.job_title, approved_job.id, colabre.settings.HOST_ROOT_URL)
			
			send_mail(
					u"Colabre | Vaga Aprovada",
                    message,
                    colabre.settings.EMAIL_FROM, 
                    [user.email], 
                    fail_silently=False)
			return HttpResponse("vaga aprovada")
		else:
			return HttpResponse("vaga não aprovada")
	except Exception, ex:
		return HttpResponse(ex.message)


