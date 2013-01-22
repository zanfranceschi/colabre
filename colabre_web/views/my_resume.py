﻿from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from colabre_web.models import *
from colabre_web.forms import *
from helpers import *
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.my_resume',
	
	url(r'^$', 'index', name='my_resume_index'),
)

def get_template_path(template):
	return 'my-resume/%s' % template

@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def index(request):
	if request.method == 'POST':
		form = ResumeForm(request.POST, profile=request.user.get_profile())
		if form.is_valid():
			form.save()
			messages.success(request, 'Currículo atualizado.')
	else:
		form = ResumeForm(profile=request.user.get_profile())
	return render(request, get_template_path('index.html'), {'form' : form })