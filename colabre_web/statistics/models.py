from django.core import serializers
from pymongo import MongoClient
from datetime import *
import sys

class RequestLogger:

	@classmethod
	def log(cls, request):
		http_access = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None
		
		access = {
			'HTTP_REFERER' 				: http_access,
			'PROCESSOR_IDENTIFIER' 		: request.META['PROCESSOR_IDENTIFIER'],
			'REQUEST_METHOD' 			: request.META['REQUEST_METHOD'],
			'QUERY_STRING' 				: request.META['QUERY_STRING'],
			'HTTP_USER_AGENT' 			: request.META['HTTP_USER_AGENT'],
			'HTTP_COOKIE' 				: request.META['HTTP_COOKIE'],
			'REMOTE_ADDR' 				: request.META['REMOTE_ADDR'],
			'PROCESSOR_ARCHITECTURE' 	: request.META['PROCESSOR_ARCHITECTURE'],
			'CSRF_COOKIE' 				: request.META['CSRF_COOKIE'],
			'PATH_INFO' 				: request.META['PATH_INFO'],
			'HTTP_ACCEPT_LANGUAGE' 		: request.META['HTTP_ACCEPT_LANGUAGE'],
			'NUMBER_OF_PROCESSORS' 		: request.META['NUMBER_OF_PROCESSORS'],
			'OS' 						: request.META['NUMBER_OF_PROCESSORS'],
			'ACCESS_DATETIME' 			: datetime.now(),
			}
			
		connection = MongoClient()
		db = connection.colabre
		db.accesses.insert(access)

class JobViewLogger:
	
	@classmethod
	def log(cls, request, search_term, job):
		session_id = 'job_viewer_logger-', job.id
		if session_id not in request.session:
			request.session[session_id] = True
			username = request.user.username if request.user else None
			user_id = request.user.id if request.user else None
			job_view = {
				'job_id' 								: job.id,
				'job_profile_id' 						: job.profile.id,
				'job_user_id' 							: job.profile.user.id,
				'job_username' 							: job.profile.user.username,
				'segment_name' 							: job.segment_name,
				'job_title_name' 						: job.job_title_name,
				'workplace_political_location_name' 	: job.workplace_political_location_name,
				'company_name'							: job.company_name,
				'creation_date'							: job.creation_date,
				'viewer_user'							: username,
				'search_term'							: search_term.lower(),
				'view_date' 							: str(datetime.now().date()),
				'view_time' 							: str(datetime.now().time()),
				'http_cookie' 							: request.META['HTTP_COOKIE'],
				'remote_addr' 							: request.META['REMOTE_ADDR'],
			}
			connection = MongoClient()
			db = connection.colabre
			db.jobviews.insert(job_view)
		
		