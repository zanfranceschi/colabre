from django.shortcuts import render
from django.http import HttpResponse
from colabre_web.models import *
import traceback
from django.contrib import messages
import time
from datetime import datetime
from django.core.signals import request_started
from django.dispatch import receiver
from gadjo.requestprovider.signals import get_request

is_not_verified_url = '/meu-perfil/solicitar-verificacao/'

def is_verified(user):
	return user.get_profile().is_verified

@receiver(request_started)
def signal_callback(sender, **kwargs):
	http_request = get_request()
	print "\n\n", http_request.META['PATH_INFO']
		
	
def handle_exception(method):
	def wrapper(request, *args):
		try:
			'''
			HTTP_REFERER: http://127.0.0.1:8000/
			PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 42 Stepping 7, GenuineIntel
			REQUEST_METHOD: GET
			QUERY_STRING:
			CONTENT_LENGTH:
			HTTP_USER_AGENT: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)
			HTTP_CONNECTION: Keep-Alive
			HTTP_COOKIE: csrftoken=Htyt4gjAbZqr8QymuN0gu1S3sjKDKBsf; sessionid=116e386558a8c80b8291e62aa2954c09
			REMOTE_ADDR: 127.0.0.1
			PROCESSOR_ARCHITECTURE: AMD64
			CSRF_COOKIE: Htyt4gjAbZqr8QymuN0gu1S3sjKDKBsf
			HTTP_HOST: 127.0.0.1:8000
			PATH_INFO: /
			HTTP_ACCEPT_LANGUAGE: pt-BR
			NUMBER_OF_PROCESSORS: 4
			OS: Windows_NT
			
			for header in request.META:
				try:
					print >> sys.stderr, "%s: %s" % (header, request.META[header])
				except KeyError, e:
					pass
			'''
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