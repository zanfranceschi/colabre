from django.db import models
from colabre_web.models import Job, Resume
from colabre_web.utils import strip_specialchars

class Statistics(object):
	is_statistics = True

class JobStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	job_id = models.IntegerField()
	profile_id = models.IntegerField(null=True)
	job_creation_date = models.DateTimeField()
	segment_id = models.IntegerField()
	segment_name = models.CharField(max_length=50)
	job_title_id = models.IntegerField()
	job_title_name = models.CharField(max_length=50)
	access_date = models.DateField(auto_now_add=True)
	access_datetime = models.DateTimeField(auto_now_add=True)
	search_term = models.CharField(max_length=50, null=True)
	session_key = models.CharField(max_length=32)
	
	def save(self, *args, **kwargs):
		if (not self.job_id):
			raise Exception("job_id cannot be null")
		
		job = Job.objects.get(id=self.job_id)
		
		if (job.profile):
			self.profile_id = job.profile.id

		self.job_creation_date = job.creation_date
		self.segment_id = job.job_title.segment.id
		self.segment_name = job.job_title.segment.name
		self.job_title_id = job.job_title.id
		self.job_title_name = job.job_title.name

		self.search_term = strip_specialchars(self.search_term)

		super(JobStatistics, self).save(*args, **kwargs)


class ResumeStatistics(models.Model, Statistics):
	class Meta:
		app_label = 'colabre_web'
		
	resume_id = models.IntegerField()
	segment_id = models.IntegerField()
	segment_name = models.CharField(max_length=50)
	access_date = models.DateField(auto_now_add=True)
	access_datetime = models.DateTimeField(auto_now_add=True)
	search_term = models.CharField(max_length=50, null=True)
	session_key = models.CharField(max_length=32)
	
	def save(self, *args, **kwargs):
		if (not self.resume_id):
			raise Exception("resume_id cannot be null")
		
		resume = Resume.objects.get(id=self.resume_id)
	
		self.segment_id = resume.segment.id
		self.segment_name = resume.segment.name
		self.search_term = strip_specialchars(self.search_term)

		super(ResumeStatistics, self).save(*args, **kwargs)
		
		
