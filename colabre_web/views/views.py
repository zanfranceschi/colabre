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
from chartit import DataPool, Chart


@handle_exception
def handle_uploaded_file(f):
	with open('some/file/name.txt', 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

@handle_exception
def legal(request):
	return render(request, 'legal.html')


def chart_test(request):
	pass
