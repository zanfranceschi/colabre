import thread
from django.contrib import messages
from django.contrib.sessions.models import Session
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import RequestLog, JobPublicNumViews, JobTermPublicNumViews
from django.core.urlresolvers import resolve
import datetime

logger = logging.getLogger('app')

def get_date_str(): 
	return str(datetime.datetime.now().date())

class StatisticsMiddleware:
	
	def process_request(self, request):
		thread.start_new_thread(self.compute_statistics, (request,))
		
	def compute_statistics(self, request):
		self.log_request(request)
		self.log_job_public_view_request(request)
		self.log_job_public_search_request(request)
		
	def has_not_been_logged(self, key, request):
		"""
			Checks if certain key has been added to the users session
			Prevents duplicated
		"""
		session_key = request.session.session_key
		session = Session.objects.get(pk=session_key)
		decoded_session = session.get_decoded()
		key += '-' + get_date_str()
		key_exists_in_session = (key in decoded_session.keys())
		if (not key_exists_in_session):
			decoded_session[key] = True
			session.session_data = Session.objects.encode(decoded_session)
			session.save()
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
		except Exception, ex:
			logger.exception(ex.message)
		
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
					logger.debug('log_job_public_search_request logged')
		except Exception, ex:
			logger.exception(ex.message)
		
	def log_job_public_view_request(self, request):
		"""
			Log public view of a jog (job details)
		"""
		try:
			if ('vagas' in request.path and resolve(request.path).func.__name__ == 'partial_details'):
				job_id = resolve(request.path).args[0]
				if self.has_not_been_logged('job_view-' + job_id, request):
					JobPublicNumViews.log(int(job_id))
					logger.debug('log_job_public_view_request logged')
		except Exception, ex:
			logger.exception(ex.message)
		
		
class HandleErrorMiddleware:
	def process_exception(self, request, exception):
		logging.error(traceback.format_exc())
		messages.error(request, traceback.format_exc())
		if request.is_ajax():
			return HttpResponse('{ "error" : "%s" }' % exception.message)
		else:
			return render(request, 'error.html')
