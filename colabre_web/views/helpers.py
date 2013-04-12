from django.shortcuts import render
from django.http import HttpResponse
from colabre_web.models import *
import traceback
import logging
from django.contrib import messages
import time
from datetime import datetime
from django.dispatch import receiver
import sys

is_not_verified_url = '/meu-perfil/solicitar-verificacao/'

def is_verified(user):
	return user.get_profile().is_verified


def not_from_oauth(user):
	return not user.get_profile().is_from_oauth
	

def handle_exception(method):
	def wrapper(request, *args):
		try:
			return method(request, *args)
		except Exception, e:
			logging.error(traceback.format_exc())
			messages.error(request, traceback.format_exc())
			if request.is_ajax():
				return HttpResponse('{ "error" : "%s" }' % e.message)
			else:
				return render(request, 'error.html')
	return wrapper
	
def decorator_with_arguments(arg1, arg2):
	def method_wrapper(method):
		def args_wrapper(request, *args):
			return render(request, 'legal.html')
			return method(request, *args)
		return args_wrapper
	return method_wrapper