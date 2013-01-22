from django.http import HttpResponse
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

urlpatterns = patterns('colabre_web.views.resumes',
	url(r'^$', 'index', name='resumes_index'),
	
	url(r'^parcial/buscar/([\d]+)/(.+)/$', 'partial_html_search'),
	url(r'^parcial/buscar/(.+)/$', 'partial_html_search'),
	url(r'^parcial/buscar/$', 'partial_html_search'),
)

def get_template_path(template):
	return 'resumes/%s' % template


@handle_exception
def index(request):
	return render(request, get_template_path('index.html'))


@handle_exception
def partial_html_search(request, before_id=0, q=None):
	resumes, exists = Resume.view_search_public(before_id, q, 100)
	return render(request, get_template_path("partial/resumes.html"), {'resumes' : resumes, 'exists': exists, 'q' : q})
