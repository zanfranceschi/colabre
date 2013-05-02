#from django.core import serializers
from django.db import models
from colabre_web.models import Job, JobTitle
import datetime
from time import strptime
import pygeoip

GEOIP_DATAFILE_PATH = 'C:/Users/zanfranceschi/Projects/Colabre/svn/data/GeoLiteCity.dat'

def get_time_range():
	now = datetime.datetime.now().time()
	frmt = "%H:%M"
	now_string = "{0}:{1}".format(now.hour, now.minute)
	now = strptime(now_string, frmt)
	
	range_0600_0959 = strptime("06:00", frmt) < now < strptime("09:59", frmt)  
	range_1000_1359 = strptime("10:00", frmt) < now < strptime("13:59", frmt) 
	range_1400_1759 = strptime("14:00", frmt) < now < strptime("17:59", frmt)
	range_1800_2159 = strptime("18:00", frmt) < now < strptime("21:59", frmt)
	
	if range_0600_0959:
		return 1
	elif range_1000_1359:
		return 2
	elif range_1400_1759:
		return 3
	elif range_1800_2159:
		return 4
	else:
		return 5

class Statistics(object):
	is_statistics = True

class JobSegmentCountStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		managed=False
		
	profile_id = models.IntegerField()
	total = models.IntegerField()
	segment_name = models.CharField(max_length=50)
	date = models.CharField(max_length=7)

class JobStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	job_id = models.IntegerField()

	profile_id = models.IntegerField()
	
	job_creation_date = models.DateTimeField()
	
	segment_id = models.IntegerField()
	segment_name = models.CharField(max_length=50)
	
	job_title_id = models.IntegerField()
	job_title_name = models.CharField(max_length=50)
	
	access_date = models.DateField(auto_now_add=True)
	access_datetime = models.DateTimeField(auto_now_add=True)
	search_term = models.CharField(max_length=50, null=True)
	
	def save(self, *args, **kwargs):
		if (not self.job_id):
			raise Exception("job_id cannot be null")
		
		job = Job.objects.get(id=self.job_id)
		
		self.profile_id = job.profile.id
		self.job_creation_date = job.creation_date
		self.segment_id = job.job_title.segment.id
		self.segment_name = job.job_title.segment.name
		self.job_title_id = job.job_title.id
		self.job_title_name = job.job_title.name
		
		super(JobStatistics, self).save(*args, **kwargs)


class ResumeStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	resume_id = models.IntegerField()
	access_date = models.DateField(auto_now_add=True)
	access_datetime = models.DateTimeField(auto_now_add=True)
	search_term = models.CharField(max_length=50, null=True)


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
		

class JobPublicNumViews(models.Model, Statistics):
	"""
		Number of public views per session of a Job
	"""
	class Meta:
		app_label = 'colabre_web'
	
	job_id = models.IntegerField(primary_key=True)
	job_title_name = models.CharField(max_length=60, null=True)
	num_views_total = models.IntegerField(default=0)
	num_views_0600_0959 = models.IntegerField(default=0)
	num_views_1000_1359 = models.IntegerField(default=0)
	num_views_1400_1759 = models.IntegerField(default=0)
	num_views_1800_2159 = models.IntegerField(default=0)
	num_views_2200_0559 = models.IntegerField(default=0)
	
	@classmethod
	def log(cls, job_id):
		if job_id is None:
			raise Exception('job_id cannot be None')
		
		logs = JobPublicNumViews.objects.filter(job_id=job_id)
		log = logs[0] if logs else JobPublicNumViews(job_id=job_id)
		log.num_views_total += 1
		
		job = Job.objects.get(id=job_id)
		job_title = job.job_title
		
		log.job_title_name = job_title.name
		
		time_range = get_time_range()
		
		if (time_range == 1):
			log.num_views_0600_0959 += 1
		elif (time_range == 2):
			log.num_views_1000_1359 += 1
		elif (time_range == 3):
			log.num_views_1400_1759 += 1
		elif (time_range == 4):
			log.num_views_1800_2159 += 1
		elif (time_range == 5):
			log.num_views_2200_0559 += 1
		log.save()


class JobTermPublicNumViews(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	job_id = models.IntegerField()
	num_views = models.IntegerField(default=0)
	search_term = models.CharField(max_length=50, blank=True, null=True)
	
	@classmethod
	def log(cls, job_id, term):
		if job_id is None:
			raise Exception('job_id cannot be None')
		
		if not term:
			term = ''
		else:
			term = term.strip().title()[:50]
		
		logs = JobTermPublicNumViews.objects.filter(job_id=job_id, search_term=term)
		log = logs[0] if logs else JobTermPublicNumViews(job_id=job_id, search_term=term)
		log.num_views += 1
		log.save()


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