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
from django.core import serializers
from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_web.views.stats',
    url(r'^parcial/vaga/detalhar/(\d+)/$', 'partial_job_details'),
)

def get_mongo_db():
    connection = MongoClient('127.0.0.1', 27017)
    return connection.colabre

def partial_job_details(request, id):
    data = {  }