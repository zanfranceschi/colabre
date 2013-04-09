import sys
import time
import thread
from django.contrib import messages
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse

class ColabreMiddleware:
	def process_request(self, request):
		thread.start_new_thread(self.test, ())
		return None
	
	def test(self):
		pass
			
class HandleErrorMiddleware:
	def process_exception(self, request, exception):
		logging.error(traceback.format_exc())
		messages.error(request, traceback.format_exc())
		print >> sys.stderr, request.is_ajax() 
		if request.is_ajax():
			return HttpResponse('{ "error" : "%s" }' % exception.message)
		else:
			return render(request, 'error.html')
