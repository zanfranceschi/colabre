import sys
import thread
from django.contrib import messages
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import RequestLog, JobPublicNumViews, JobTermPublicNumViews
from django.core.urlresolvers import reverse, resolve
import datetime

def get_date_str(): 
	return str(datetime.datetime.now().date())

class StatisticsMiddleware:
	
	def process_request(self, request):
		self.start_computing_statistics(request)
		
	def ensure_session_key(self, request):
		"""
			Workaround to make sure there's a session_key
		"""
		if (request.session.session_key is None):
			"""
				Explicit requested pages to create the key...
			"""
			pages = ['jobs_index', 'resumes_index', 'login', 'registration_index', 'home_index', 'home_legal']
			current_page = resolve(request.path).func.__name__
			if (any(current_page in page for page in pages)):
				request.session['ensured_session_key'] = True
				
	def start_computing_statistics(self, request):
		"""
			Simple delegate method to start the statistics collection
		"""
		self.ensure_session_key(request)
		self.compute_statistics(request)
		
	def compute_statistics(self, request):
		"""
			Statistics collection in a multi-threaded fashion
		"""
		thread.start_new_thread(self.log_request, (request,))
		thread.start_new_thread(self.log_job_public_view_request, (request,))
		thread.start_new_thread(self.log_job_public_search_request, (request,))
		#thread.start_new_thread(self.test, (request,))
		
	def test(self, request):
		now = datetime.datetime.now().time()
		now_string = "{0}:{1}:{2}".format(now.hour, now.minute, now.second)
		print >> sys.stderr, now_string
	
	def has_not_been_logged(self, key, request):
		"""
			Prevents duplicated
		"""
		key += '-' + get_date_str()
		key_exists_in_session = (key in request.session)
		#if (not key_exists_in_session):
		request.session[key] = True
		return not key_exists_in_session
	
	def log_request(self, request):
		"""
			Simple request log
			Log every single request...
		"""
		try:
			log = RequestLog()
			log.request = request
			log.save()
		except:
			pass
		
	def log_job_public_search_request(self, request):
		"""
			Log public view of a jog (job details) per search term
		"""
		try:
			if ('vagas' in request.path and resolve(request.path).func.__name__ == 'partial_details'):
				job_id = resolve(request.path).args[0]
				term = resolve(request.path).args[1]
				if self.has_not_been_logged('job_view-' + term + job_id, request):
					JobTermPublicNumViews.log(int(job_id), term)
		except Exception, ex:
			raise ex
		
	def log_job_public_view_request(self, request):
		"""
			Log public view of a jog (job details)
		"""
		try:
			if ('vagas' in request.path and resolve(request.path).func.__name__ == 'partial_details'):
				job_id = resolve(request.path).args[0]
				if self.has_not_been_logged('job_view-' + job_id, request):
					JobPublicNumViews.log(int(job_id))
					import sys
					print >> sys.stderr, 'LOGGED'
		except Exception, ex:
			raise ex
		

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
