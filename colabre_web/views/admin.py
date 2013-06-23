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
from django.core.urlresolvers import reverse
import sys
from urlparse import urljoin
import shortuuid


logger = logging.getLogger('app')


urlpatterns = patterns('colabre_web.views.admin',
	url(r'^vaga/aprovar/(\d+)/(.+)$', 'job_approve', name='admin_job_approve'),
)

def get_template_path(template):
	return 'jobs/%s' % template


def job_approve(request, id, uuid):
	try:
		approved_job = Job.objects.get(id=id, uuid=uuid, admin_approved=False)
		approved_job.admin_approved = True
		approved_job.uuid = shortuuid.uuid()
		approved_job.admin_approval_date = datetime.now()
		approved_job.save()
		
		sub_message = None
		
		if (approved_job.contact_email_verified):
			sub_message = u"Você pode vê-la em {0}".format(urljoin(
															colabre.settings.HOST_ROOT_URL, 
															reverse('colabre_web.views.jobs.detail', args=(approved_job.id,))
														)
													)
		else:
			sub_message = u"Entretanto, é necessário que este email seja verificado. Entre em {0} e informe o código: {1}".format(urljoin(
															colabre.settings.HOST_ROOT_URL, 
															reverse('colabre_web.views.jobs.validade_email', args=(approved_job.id,approved_job.contact_email,))
														)
													)

		message = u"""{0},

Obrigado por usar o Colabre! Acabamos de aprovar sua vaga para {1}.
{2}

Abraços,

Equipe Colabre
www.colabre.org
""".format(
		approved_job.contact_name, 
		approved_job.job_title,
		sub_message 
		)

		send_mail(
					u"Colabre | Vaga Aprovada",
                    message,
                    colabre.settings.EMAIL_FROM, 
                    [approved_job.contact_email], 
                    fail_silently=False)
		return HttpResponse("vaga aprovada")
	except Exception, ex:
		raise ex
		return HttpResponse(ex.message)


