import sys
import thread
from django.contrib import messages
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import RequestLog
from django.core.urlresolvers import reverse


class ColabreMiddleware:
	def process_request(self, request):
		thread.start_new_thread(self.test, (request,))
		return None
	
	def test(self, request):
		log = RequestLog()
		log.request = request
		log.save()
		
		if request.path == reverse('jobs_partial_html_search') and request.method == 'POST':
			term = request.POST.get('term')
			if term:
				print >> sys.stderr, term
			
class HandleErrorMiddleware:
	def process_exception(self, request, exception):
		logging.error(traceback.format_exc())
		messages.error(request, traceback.format_exc())
		if request.is_ajax():
			return HttpResponse('{ "error" : "%s" }' % exception.message)
		else:
			return render(request, 'error.html')
