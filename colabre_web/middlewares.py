import sys
import thread
from django.contrib import messages
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import RequestLog, JobPublicNumViews
from django.core.urlresolvers import reverse, resolve


class ColabreMiddleware:
	def process_request(self, request):
		thread.start_new_thread(self.compute_statistics, (request,))
		return None
	
	def ensure_session_key(self, request):
		pages = ['jobs_index', 'resumes_index', 'login', 'registration_index', 'home_index', 'home_legal']
		current_page = resolve(request.path).func.__name__
		if any(current_page in page for page in pages):
			request.session['ensured_session_key'] = True
	
		if request.session.session_key is None:
			request.session['ensured_session_key'] = True

			
	def compute_statistics(self, request):
		try:
			request.session['x'] = 1
			print >> sys.stderr, "-" * 60
			print >> sys.stderr, request.session.session_key
			print >> sys.stderr, "-" * 60
			#self.log_request(request)
			#self.log_job_public_view_request(request)
		except Exception as ex:
			print >> sys.stderr, ex.message
		
		
	def log_job_public_view_request(self, request):
		if (resolve(request.path).func.__name__ == 'partial_details'):
			job_id = resolve(request.path).args[0]
			obj = JobPublicNumViews()
			obj.job_id = int(job_id)
			obj.request = request
			obj.save()
	
	def log_request(self, request):
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
