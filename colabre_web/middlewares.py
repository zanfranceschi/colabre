import thread
import sys
from django.contrib import messages
from django.contrib.sessions.models import Session
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import RequestLog, JobPublicNumViews, JobTermPublicNumViews, MyResumeStatistics
from django.core.urlresolvers import resolve
import datetime

from django.utils import simplejson as json

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
		self.log_resume_request(request)
		
	def log_resume_request(self, request):
		try:
			resolved = resolve(request.path)
			if (resolved.url_name == 'resumes_partial_details'):
				resume_id = resolved.args[0]
				search_term = resolved.args[1]
				log = MyResumeStatistics(resume_id=resume_id, search_term=search_term)
				log.save()
		except Exception, ex:
			logger.exception(ex.message)
			

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
			print >> sys.stderr, "-" * 60
			if (request.method == 'POST'):
				for key, value in request.POST.iteritems():
					print >> sys.stderr, "{0}: {1}".format(key, value)
				print >> sys.stderr, json.dumps(request.POST)
			elif (request.method == 'GET'):
				for key, value in request.GET.iteritems():
					print >> sys.stderr, "{0}: {1}".format(key, value)
				print >> sys.stderr, json.dumps(request.GET) 
			print >> sys.stderr, "-" * 60
					
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
