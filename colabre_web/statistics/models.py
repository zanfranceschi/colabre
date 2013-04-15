#from django.core import serializers
from django.db import models
import datetime
import pygeoip

GEOIP_DATAFILE_PATH = 'C:/Users/zanfranceschi/Projects/Colabre/svn/data/GeoLiteCity.dat'

class Statistics(object):
	is_statistics = True

class RequestLog(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
	
	request = None
	
	http_referer = models.URLField(max_length=200, null=True)
	request_method = models.CharField(max_length=6)
	query_string = models.CharField(max_length=200)
	http_user_agent = models.CharField(max_length=300)
	remote_addr = models.CharField(max_length=200)
	session_id = models.CharField(max_length=200)
	path_info = models.CharField(max_length=200)
	access_datetime = models.DateTimeField(auto_now_add=True)
	
	def get_geo_info(self):
		gic = pygeoip.GeoIP(GEOIP_DATAFILE_PATH)
		return gic.record_by_addr(self.remote_addr)
	
	def save(self, *args, **kwargs):
		if self.request is None:
			raise Exception('self.request cannot be None')
		
		http_access = self.request.META['HTTP_REFERER'] if 'HTTP_REFERER' in self.request.META else None
		self.http_referer = http_access
		self.request_method = self.request.META['REQUEST_METHOD']
		self.query_string = self.request.META['QUERY_STRING']
		self.http_user_agent = self.request.META['HTTP_USER_AGENT']
		self.remote_addr = self.request.META['REMOTE_ADDR']
		self.session_id = self.request.session.session_key or '--'
		self.path_info = self.request.META['PATH_INFO']
		self.access_datetime = datetime.datetime.now()

		super(RequestLog, self).save(*args, **kwargs)
		
class JobStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	job_id = models.IntegerField()
	views = models.IntegerField()


class JobPublicNumViews(models.Model, Statistics):
	"""
		Number of public views per session of a Job
	"""
	class Meta:
		app_label = 'colabre_web'
	
	request = None
	job_id = models.IntegerField()
	num_views = models.IntegerField()
	
	def save(self, *args, **kwargs):
		if self.request is None:
			raise Exception('self.request cannot be None')
		
		if self.job_id is None:
			raise Exception('self.job_id cannot be None')
		
		session_name = 'job-' + str(self.job_id) + '-viewed'
		
		if (session_name not in self.request.session):
			try:
				obj = JobPublicNumViews.objects.get(job_id=self.job_id)
				self.num_views = obj.num_views + 1
				super(JobPublicNumViews, self).save(*args, **kwargs)
				self.request.session[session_name] = True
			except JobPublicNumViews.DoesNotExist:
				pass

class LogObjectFactory:
	@classmethod
	def log_job_request(cls, request, search_term, job):
		username = request.user.username if request.user else None
		user_id = request.user.id if request.user else None
		dt = datetime.datetime.now()
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