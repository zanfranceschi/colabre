#from django.core import serializers
from tasks import *

class LogObjectFactory:
	@classmethod
	def log_request(cls, request):
		http_access = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None
		return {
			'http_referer'			: http_access,
			'request_method'		: request.META['REQUEST_METHOD'],
			'query_string'			: request.META['QUERY_STRING'],
			'http_user_agent'		: request.META['HTTP_USER_AGENT'],
			'remote_addr'			: request.META['REMOTE_ADDR'],
			'csrf_cookie'			: request.META['CSRF_COOKIE'],
			'path_info'				: request.META['PATH_INFO'],
			'http_accept_language'	: request.META['HTTP_ACCEPT_LANGUAGE'],
			'access_datetime'		: datetime.now(),
			'access_date'			: str(datetime.now().date()),
		}

	@classmethod
	def log_job_request(cls, request, search_term, job):
		username = request.user.username if request.user else None
		user_id = request.user.id if request.user else None
		dt = datetime.now()
		search_term = search_term.lower().strip()
		return {
            'job_id'							: job.id,
            'job_profile_id'					: job.profile.id,
            'job_user_id'						: job.profile.user.id,
            'job_username'						: job.profile.user.username,
            'segment_name'						: job.segment_name,
            'job_title_name'					: job.job_title_name,
            'location'							: str(job.location),
            'company_name'						: job.company_name,
            'creation_date'						: job.creation_date,
            'viewer_user_id'					: user_id,
            'viewer_user'						: username,
            'search_term'						: search_term.lower(),
            'http_cookie'						: request.META['HTTP_COOKIE'],
            'remote_addr'						: request.META['REMOTE_ADDR'],
            'date_year'							: dt.year,
            'date_month'						: dt.month,
            'date_week'							: dt.isocalendar()[1],
            'date_hour'							: dt.hour,
            'date_day'							: dt.day,
            'date_date'							: str(dt.date()),
            'date_time'							: dt,
        }
	

def log_request(request):
	log = LogObjectFactory.log_request(request)
	celery_log_request.delay(log)

def log_job_request(request, search_term, job):
	log = LogObjectFactory.log_job_request(request, search_term, job)
	celery_log_job_request.delay(log)
	
def log_resume_request(request, search_term, resume):
	pass
	#celery_log_resume_request.delay(request, search_term, resume)