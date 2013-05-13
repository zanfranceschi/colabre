import thread
from django.contrib import messages
import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponse
from statistics.models import ResumeStatistics, JobStatistics
from django.core.urlresolvers import resolve
import datetime
import sys

logger = logging.getLogger('app')

def get_date_str():
	return str(datetime.datetime.now().date())

class StatisticsMiddleware:

	def process_request(self, request):
		thread.start_new_thread(self.compute_statistics, (request,))
		
	def compute_statistics(self, request):
		self.log_resume_request(request)
		self.log_job_request(request)
		
	def log_resume_request(self, request):
		try:
			resolved = resolve(request.path)
			if (resolved.url_name == 'resumes_partial_details'):
				resume_id = resolved.args[0]
				search_term = resolved.args[1]
				if (self.has_not_been_logged('resume' + resume_id + search_term, request)):
					log = ResumeStatistics(resume_id=resume_id, search_term=search_term, session_key=request.session.session_key)
					log.save()
		except:
			logger.exception("-- colabre_web/middlewares.py, StatisticsMiddleware.log_resume_request --")
			
			
	def log_job_request(self, request):
		try:
			resolved = resolve(request.path)
			if (resolved.url_name == 'jobs_partial_details'):
				job_id = resolved.args[0]
				search_term = resolved.args[1]
				if (self.has_not_been_logged('job' + job_id + search_term, request)):
					log = JobStatistics(job_id=job_id, search_term=search_term, session_key=request.session.session_key)
					log.save()
		except:
			logger.exception("-- colabre_web/middlewares.py, StatisticsMiddleware.log_job_request --")
			

	def has_not_been_logged(self, key, request):
		"""
			Checks if certain key has been added to the users session
			Prevents duplicated
		"""
		key += '-' + get_date_str()
		key_exists_in_session = (key in request.session)
		if (not key_exists_in_session):
			request.session[key] = True
		return not key_exists_in_session
		
		
class HandleErrorMiddleware:
	def process_exception(self, request, exception):
		try:
			logger.exception("-- colabre_web/middlewares.py, HandleErrorMiddleware.process_exception --")
			messages.error(request, traceback.format_exc())
			if request.is_ajax():
				return HttpResponse('{ "error" : "%s" }' % exception.message)
			else:
				return render(request, 'error.html')
		except:
			logger.exception("-- colabre_web/middlewares.py, HandleErrorMiddleware.process_exception 02 --")
