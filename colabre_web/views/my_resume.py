# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from colabre_web.models import *
from colabre_web.forms import *
from colabre_web.views.my_jobs import partial_json_search_segment as my_profile_partial_json_search_segment
from helpers import *
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.my_resume',
	
	url(r'^$', 'index', name='my_resume_index'),
	url(r'^parcial/buscar-segmento/(.+)/$', 'partial_json_search_segment', name= 'my_resume_partial_json_search_segment'),
)

def get_template_path(template):
	return 'my-resume/%s' % template

@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
@handle_exception
def index(request):
	if request.method == 'POST':
		"""test"""
		import sys
		segments = request.POST.getlist('segment')
		
		for segment in segments:
			print >> sys.stderr, segment
		
		form = ResumeForm(request.POST, profile=request.user.get_profile())
		if form.is_valid():
			form.save()
			messages.success(request, u'Currículo atualizado.')
	else:
		form = ResumeForm(profile=request.user.get_profile())
	return render(request, get_template_path('index.html'), {'form' : form })

@login_required
@handle_exception
def partial_json_search_segment(request, q):
	return my_profile_partial_json_search_segment(request, q)