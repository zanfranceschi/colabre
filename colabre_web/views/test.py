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
from django.core import serializers


@handle_exception
def test(request, q):
	data = None #serializers.serialize("json", City.objects.filter(name__icontains=q).order_by("name")[:10], indent=4, relations=('state','country'))
	return HttpResponse(data, mimetype="application/json")