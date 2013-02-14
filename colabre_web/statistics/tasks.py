from datetime import datetime
from celery import Celery
from pymongo import MongoClient

celery = Celery('tasks', broker='amqp://guest@localhost//', backend='amqp')

def get_mongo_db():
	connection = MongoClient('127.0.0.1', 27017)
	return connection.colabre

@celery.task
def celery_log_request(request_META):
	http_access = request_META['HTTP_REFERER'] if 'HTTP_REFERER' in request_META else None
	req = {
		'HTTP_REFERER'               : http_access,
		'REQUEST_METHOD'             : request_META['REQUEST_METHOD'],
		'QUERY_STRING'               : request_META['QUERY_STRING'],
		'HTTP_USER_AGENT'            : request_META['HTTP_USER_AGENT'],
		'REMOTE_ADDR'                : request_META['REMOTE_ADDR'],
		'CSRF_COOKIE'                : request_META['CSRF_COOKIE'],
		'PATH_INFO'                  : request_META['PATH_INFO'],
		'HTTP_ACCEPT_LANGUAGE'       : request_META['HTTP_ACCEPT_LANGUAGE'],
		'ACCESS_DATETIME'            : datetime.now(),
		}
	db = get_mongo_db()
	db.requests.insert(req)

@celery.task
def celery_log_job_request(request, search_term, job):
	"""
		Log a job details request IF it hasn't been requested yet
		checking the session ID per job ID and IP address
	"""
	session_id = 'job_viewer_logger-', job.id, '-', request.META['REMOTE_ADDR']
	if session_id not in request.session:
		request.session[session_id] = True
		username = request.user.username if request.user else None
		user_id = request.user.id if request.user else None
		date = datetime.now()
		db = get_mongo_db()
		search_term = search_term.lower().strip()
		count_1 = { '$inc' : { 'c' : 1} }
		upsert = {'upsert' : True }
		
		# date
		job_date = {
			'jid' : job.id,
			'd'   : str(date.date()),
        }
		db.jobs_date.update(job_date, count_1, upsert)
		
		job_date_term = {
			'jid' : job.id,
			'd'   : str(date.date()),
			't'   : search_term,
        }
		db.jobs_date_term.update(job_date_term, count_1, upsert)
		
		
		# week
		job_week = {
			'jid' : job.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
        }
		db.jobs_week.update(job_week, count_1, upsert)
		
		job_week_term = {
			'jid' : job.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
			't'   : search_term,
        }
		db.jobs_week_term.update(job_week_term, count_1, upsert)
		
		# month
		job_month = {
			'jid'  : job.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
        }
		db.jobs_month.update(job_month, count_1, upsert)
		
		job_month_term = {
			'jid'  : job.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.jobs_month_term.update(job_month_term, count_1, upsert)
		
		# search date
		search_term_jobs_date = {
			'd'    : str(date.date()),
			't'    : search_term,
        }
		db.search_terms_jobs_date.update(search_term_jobs_date, count_1, upsert)
		
		# search week
		search_term_jobs_week = {
			'w'    : str(date.isocalendar()[1]),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_jobs_week.update(search_term_jobs_week, count_1, upsert)
		
		# search month
		search_term_jobs_month = {
			'm'   : str(date.month),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_jobs_month.update(search_term_jobs_month, count_1, upsert)
		
		# search year
		search_term_jobs_year = {
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_jobs_year.update(search_term_jobs_year, count_1, upsert)
		
		# search all times
		search_term_jobs_all = {
			't'    : search_term,
        }
		db.search_terms_jobs_all.update(search_term_jobs_all, count_1, upsert)
		
		# full
		job_full = {
            'job_id'                              : job.id,
            'job_profile_id'                      : job.profile.id,
            'job_user_id'                         : job.profile.user.id,
            'job_username'                        : job.profile.user.username,
            'segment_name'                        : job.segment_name,
            'job_title_name'                      : job.job_title_name,
            'workplace_political_location_name'   : job.workplace_political_location_name,
            'company_name'                        : job.company_name,
            'creation_date'                       : job.creation_date,
            'viewer_user'                         : username,
            'search_term'                         : search_term.lower(),
            'view_date'                           : str(datetime.now().date()),
            'view_time'                           : str(datetime.now().time()),
            'http_cookie'                         : request.META['HTTP_COOKIE'],
            'remote_addr'                         : request.META['REMOTE_ADDR'],
        }
		db.jobs_full.insert(job_full)

@celery.task
def celery_log_resume_request(request, search_term, resume):
	pass
	"""
		Log a resume details request IF it hasn't been requested yet
		checking the session ID per job ID and IP address
	"""
	session_id = 'resume_viewer_logger-', resume.id, '-', request.META['REMOTE_ADDR']
	if session_id not in request.session:
		request.session[session_id] = True
		username = request.user.username if request.user else None
		user_id = request.user.id if request.user else None
		date = datetime.now()
		db = get_mongo_db()
		search_term = search_term.lower().strip()
		count_1 = { '$inc' : { 'c' : 1} }
		upsert = {'upsert' : True }
		
		# date
		resume_date = {
			'rid' : resume.id,
			'd'   : str(date.date()),
        }
		db.resumes_date.update(resume_date, count_1, upsert)
		
		resume_date_term = {
			'rid' : resume.id,
			'd'   : str(date.date()),
			't'   : search_term,
        }
		db.resumes_date_term.update(resume_date_term, count_1, upsert)
		
		# week
		resume_week = {
			'rid' : resume.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
        }
		db.resumes_week.update(resume_week, count_1, upsert)
		
		resume_week_term = {
			'rid' : resume.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
			't'   : search_term,
        }
		db.resumes_week_term.update(resume_week_term, count_1, upsert)
		
		# month
		resume_month = {
			'rid'  : resume.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
        }
		db.resumes_month.update(resume_month, count_1, upsert)
		
		resume_month_term = {
			'rid'  : resume.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.resumes_month_term.update(resume_month_term, count_1, upsert)
		
		# search date
		search_term_resumes_date = {
			'd'    : str(date.date()),
			't'    : search_term,
        }
		db.search_terms_resumes_date.update(search_term_resumes_date, count_1, upsert)
		
		# search week
		search_term_resumes_week = {
			'w'    : str(date.isocalendar()[1]),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_resumes_week.update(search_term_resumes_week, count_1, upsert)
		
		# search month
		search_term_resumes_month = {
			'm'   : str(date.month),
			'y'   : str(date.year),
			't'   : search_term,
        }
		db.search_terms_resumes_month.update(search_term_resumes_month, count_1, upsert)
		
		# search year
		search_term_resumes_year = {
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_resumes_year.update(search_term_resumes_year, count_1, upsert)
		
		# search all times
		search_term_resumes_all = {
			't'    : search_term,
        }
		db.search_terms_resumes_all.update(search_term_resumes_all, count_1, upsert)
		
		# full
		resume_full = {
            'resume_id'                           : resume.id,
            'resume_profile_id'                   : resume.profile.id,
            'resume_user_id'                      : resume.profile.user.id,
            'resume_username'                     : resume.profile.user.username,
            'segment_name'                        : resume.segment_name,
            'resume_title_name'                   : resume.resume_title_name,
            'workplace_political_location_name'   : resume.workplace_political_location_name,
            'company_name'                        : resume.company_name,
            'creation_date'                       : resume.creation_date,
            'viewer_user'                         : username,
            'search_term'                         : search_term.lower(),
            'view_date'                           : str(datetime.now().date()),
            'view_time'                           : str(datetime.now().time()),
            'http_cookie'                         : request.META['HTTP_COOKIE'],
            'remote_addr'                         : request.META['REMOTE_ADDR'],
        }
		db.resumes_full.insert(resume_full)

@celery.task
def celery_test(q):
	return "\n --- ", q, " --- \n"