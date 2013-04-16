from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import *
from colabre_web.models import *
import time
from colabre_web.forms import *
from helpers import *
from django.conf.urls import patterns, url

urlpatterns = patterns('colabre_web.views.home',
	#url(r'^parcial/alguma-chamada-ajax/$', 'partial_some_ajax_call', name='home_partial_some_ajax_call'),
)

def get_template_path(template):
	return 'home/%s' % template

@handle_exception
def index(request):
	form = LoginForm()
	return render(request, get_template_path("index.html"), {'form' : form})

def legal(request):
	return render(request, get_template_path("legal.html"))