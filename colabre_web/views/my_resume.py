# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from colabre_web.forms import ResumeForm
from helpers import is_verified, is_not_verified_url
from django.conf.urls import patterns, url

urlpatterns = patterns('colabre_web.views.my_resume',
	url(r'^$', 'index', name='my_resume_index'),
)

def get_template_path(template):
	return 'my-resume/%s' % template

@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def index(request):
	if request.method == 'POST':
		
		"""test"""
		"""
		import sys
		segments = request.POST.getlist('segment')
		
		for segment in segments:
			print >> sys.stderr, segment
		"""

		form = ResumeForm(request.POST, profile=request.user.get_profile())
		if form.is_valid():
			form.save()
			messages.success(request, u'Currículo atualizado.')
	else:
		form = ResumeForm(profile=request.user.get_profile())
	return render(request, get_template_path('index.html'), {'form' : form })