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

from colabre_web.statistics.tasks import get_mongo_db

urlpatterns = patterns('colabre_web.views.contact',
	url(r'^enviar-mensagem/$', 'partial_send_message', name='contact_send_message'),
	url(r'^obter-formulario/$', 'partial_get_form', name='contact_get_form'),
)

def get_template_path(template):
	return 'jobs/%s' % template

@handle_exception
def partial_send_message(request):
	if request.method == 'POST':
		user_id = request.POST['user_id']
		cc_email = request.POST['cc_email']
		message = request.POST['message']
		response = HttpResponse(user_id)
		return response

@handle_exception
def partial_get_form(request):
	form = ContactForm()
	response = render(request, '_contact-form.html', {'form_id' : request.POST['resume_id'] })
	response['resume-id'] = request.POST['resume_id']
	return response
	