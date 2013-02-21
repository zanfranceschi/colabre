from datetime import datetime
from celery import Celery
from pymongo import MongoClient
import pygeoip
from colabre_web.statistics.settings import *

celery = Celery('tasks', broker='amqp://guest@localhost//', backend='amqp')

def get_mongo_db():
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	return connection.colabre


@celery.task
def celery_log_request(log):
	db = get_mongo_db()
	
	# Path info
	db.stats_path.update({ 'path_info' : log['path_info']}, { '$inc' : { 'c' : 1 } }, upsert=True)
	
	db.requests.insert(log)
	
	# should_log
	should_log = db.stats_should_log.find({
						'access_date' : log['access_date'],
						'remote_addr' : log['remote_addr']
						}).count() == 0
						
	if (should_log):
		db.stats_should_log.insert({
						'access_date' : log['access_date'],
						'remote_addr' : log['remote_addr']
						}) # should log no more
		
		# City
		gic = pygeoip.GeoIP(GEOIP_DATAFILE_PATH)
		record = gic.record_by_addr(log['remote_addr'])
		db.stats_city.update(record, { '$inc' : { 'c' : 1 } }, upsert=True)
		
		# Browser
		db.stats_browser.update({ 'http_user_agent' : log['http_user_agent']}, { '$inc' : { 'c' : 1 } }, upsert=True)
		
		return 'request logged'
	
	return 'request not logged'


@celery.task
def celery_log_job_request(log):
	db = get_mongo_db()
	should_log = db.jobs_full.find({ 
									'job_id' 		: log['job_id'],
									'remote_addr'	: log['remote_addr'],
									'date_date'		: log['date_date']
									}).count() == 0
	if should_log:
		count_1 = { '$inc' : { 'c' : 1 } }
		
		# date
		job_date = {
			'jid' : log['job_id'],
			'd'   : log['date_date'],
	    }
		db.jobs_date.update(job_date, count_1, upsert=True)
		
		job_date_term = {
			'jid' : log['job_id'],
			'd'   : log['date_date'],
			't'   : log['search_term'],
	    }
		db.jobs_date_term.update(job_date_term, count_1, upsert=True)
		
		# week
		job_week = {
			'jid' : log['job_id'],
			'w'   : log['date_week'],
			'y'   : log['date_year'],
	    }
		db.jobs_week.update(job_week, count_1, upsert=True)
		
		job_week_term = {
			'jid' : log['job_id'],
			'w'   : log['date_week'],
			'y'   : log['date_year'],
			't'   : log['search_term'],
	    }
		db.jobs_week_term.update(job_week_term, count_1, upsert=True)
		
		# month
		job_month = {
			'jid' : log['job_id'],
			'm'    : log['date_month'],
			'y'   : log['date_year'],
	    }
		db.jobs_month.update(job_month, count_1, upsert=True)
		
		job_month_term = {
			'jid' : log['job_id'],
			'm'    : log['date_month'],
			'y'   : log['date_year'],
			't'   : log['search_term'],
	    }
		db.jobs_month_term.update(job_month_term, count_1, upsert=True)
		
		# search date
		search_term_jobs_date = {
			'd'   : log['date_date'],
			't'   : log['search_term'],
	    }
		db.search_terms_jobs_date.update(search_term_jobs_date, count_1, upsert=True)
		
		# search week
		search_term_jobs_week = {
			'w'   : log['date_week'],
			'y'   : log['date_year'],
			't'   : log['search_term'],
	    }
		db.search_terms_jobs_week.update(search_term_jobs_week, count_1, upsert=True)
		
		# search month
		search_term_jobs_month = {
			'm'    : log['date_month'],
			'y'   : log['date_year'],
			't'   : log['search_term'],
	    }
		db.search_terms_jobs_month.update(search_term_jobs_month, count_1, upsert=True)
		
		# search year
		search_term_jobs_year = {
			'y'   : log['date_year'],
			't'   : log['search_term'],
	    }
		db.search_terms_jobs_year.update(search_term_jobs_year, count_1, upsert=True)
		
		# search all times
		search_term_jobs_all = {
			't'   : log['search_term'],
	    }
		db.search_terms_jobs_all.update(search_term_jobs_all, count_1, upsert=True)
		
		db.jobs_full.insert(log)
	
		return 'job details logged'
	
	return 'job details not logged'

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
		
		# date
		resume_date = {
			'rid' : resume.id,
			'd'   : str(date.date()),
        }
		db.resumes_date.update(resume_date, count_1, upsert=True)
		
		resume_date_term = {
			'rid' : resume.id,
			'd'   : str(date.date()),
			't'   : search_term,
        }
		db.resumes_date_term.update(resume_date_term, count_1, upsert=True)
		
		# week
		resume_week = {
			'rid' : resume.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
        }
		db.resumes_week.update(resume_week, count_1, upsert=True)
		
		resume_week_term = {
			'rid' : resume.id,
			'w'   : str(date.isocalendar()[1]),
			'y'   : str(date.year),
			't'   : search_term,
        }
		db.resumes_week_term.update(resume_week_term, count_1, upsert=True)
		
		# month
		resume_month = {
			'rid'  : resume.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
        }
		db.resumes_month.update(resume_month, count_1, upsert=True)
		
		resume_month_term = {
			'rid'  : resume.id,
			'm'    : str(date.month),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.resumes_month_term.update(resume_month_term, count_1, upsert=True)
		
		# search date
		search_term_resumes_date = {
			'd'    : str(date.date()),
			't'    : search_term,
        }
		db.search_terms_resumes_date.update(search_term_resumes_date, count_1, upsert=True)
		
		# search week
		search_term_resumes_week = {
			'w'    : str(date.isocalendar()[1]),
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_resumes_week.update(search_term_resumes_week, count_1, upsert=True)
		
		# search month
		search_term_resumes_month = {
			'm'   : str(date.month),
			'y'   : str(date.year),
			't'   : search_term,
        }
		db.search_terms_resumes_month.update(search_term_resumes_month, count_1, upsert=True)
		
		# search year
		search_term_resumes_year = {
			'y'    : str(date.year),
			't'    : search_term,
        }
		db.search_terms_resumes_year.update(search_term_resumes_year, count_1, upsert=True)
		
		# search all times
		search_term_resumes_all = {
			't'    : search_term,
        }
		db.search_terms_resumes_all.update(search_term_resumes_all, count_1, upsert=True)
		
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