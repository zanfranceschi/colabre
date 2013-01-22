from django.shortcuts import render
from django.http import HttpResponse
from colabre_web.models import *
import traceback
from django.contrib import messages
import time

is_not_verified_url = '/meu-perfil/solicitar-verificacao/'

def is_verified(user):
	return user.get_profile().is_verified

def handle_exception(method):
	def wrapper(request, *args):
		try:
			return method(request, *args)
		except Exception, e:
			print >> sys.stderr, "-" * 60
			print >> sys.stderr, traceback.format_exc()
			print >> sys.stderr, "-" * 60
			messages.error(request, e.message)
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