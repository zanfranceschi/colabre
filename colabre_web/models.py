# -*- coding: UTF-8 -*-
from aux_models import *
from django.db import models, connection
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import authenticate
from django.template.loader import get_template
from django.template import Context
import uuid
from datetime import *
import time
from django.core.mail import send_mail
import colabre.settings
import sys

def dictfetchall(cursor):
	"Returns all rows from a cursor as a dict"
	desc = cursor.description
	return [
		dict(zip([col[0] for col in desc], row))
		for row in cursor.fetchall()
	]

class UserProfile(models.Model):
	""" Binds Django user to resume and jobs """
	#company = models.ForeignKey('domain.Company')
	user = models.ForeignKey(User, unique=True)
	is_verified = models.BooleanField(default=False)
	profile_type = models.CharField(max_length=2, choices=(('js', 'Buscar Vagas'), ('jp', 'Publicar Vagas')))
	gender = models.CharField(default='U', max_length=1, choices=(('U', 'Indefinido'), ('F', 'Feminino'), ('M', 'Masculino')))
	
	birth_year = models.IntegerField(null=True)
	birth_month = models.IntegerField(null=True)
	birth_day = models.IntegerField(null=True)
	
	active = models.BooleanField(default=True)
	def set_password(self, password):
		self.user.set_password(password)
		self.user.save()

	@staticmethod
	def retrieve_access(username_or_email):
		try:
			user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
			um = UserManager()
			new_password = um.make_random_password(6, user.username)
			user.set_password(new_password)
			user.save()
			UserNotification.getNotification().notify_password_change(user, new_password)
			return True
		except User.DoesNotExist:
			return False

	@staticmethod
	def get_profile_by_user(user):
		return UserProfile.objects.get(user=user)

	@property
	def resume(self):
		try:
			return Resume.objects.get(profile=self)
		except Resume.DoesNotExist:
			pass

	@property
	def jobs(self):
		return Job.objects.filter(profile=self)
		

	def __unicode__(self):
		return "%s %s (%s)" % (self.user.first_name, self.user.last_name, self.user.username)
	
	@staticmethod
	def create(username, email, password):
		# Associate to a Django user
		new_user = User()
		new_user.is_superuser = False
		new_user.is_staff = False
		new_user.is_active = True
		new_user.username = new_user.first_name = username
		new_user.email = email
		new_user.set_password(password)
		new_user.save()
		profile = UserProfile()
		profile.user = new_user
		profile.is_verified = False
		profile.save()
		UserProfileVerification.create(profile)
		
		return profile
		
	
	@staticmethod
	def update_profile(
					user, 
					first_name, 
					last_name, 
					email, 
					profile_type, 
					gender,
					birth_year,
					birth_month, 
					birth_day):

		profile = UserProfile.objects.get(user=user)
		profile.user.first_name = first_name
		profile.user.last_name = last_name
	
		new_email = email
		if new_email != profile.user.email and profile.is_verified:
			verification = UserProfileVerification.objects.get(profile=profile)
			verification.uuid = str(uuid.uuid4())
			verification.save()
			UserNotification.getNotification().notify(profile, verification.uuid)
			profile.is_verified = False
		profile.user.email = email
	
		profile.profile_type = profile_type
		profile.gender = gender
		profile.birth_year = birth_year
		profile.birth_month = birth_month
		profile.birth_day = birth_day
		profile.save()


	def save(self, *args, **kwargs):
		user = User.objects.get(id=self.user.id)
		if user.email != self.user.email:
			self.is_verified = False
		super(UserProfile, self).save(*args, **kwargs)
		self.user.save()


class Resume(models.Model):
	profile = models.ForeignKey(UserProfile, unique=True)
	short_description = models.TextField(max_length=255)
	full_description = models.TextField()
	visible = models.BooleanField(default=True)
	active = models.BooleanField(default=True)
	@staticmethod
	def view_search_public(after_id, q, limit):
		query_id = Q(id__lt=after_id)
		if after_id == '0' or after_id == 0:
			query_id = Q()
			
		query_description = Q(
			Q(short_description__icontains=q) | 
			Q(full_description__icontains=q)
		)
		if q == None:
			query_description = Q()
		
		visible_query = Q(visible=True)
		
		resumes = Resume.objects.filter(visible_query, query_id, query_description).order_by("-id")[:limit]
		exists = Resume.objects.filter(visible_query, query_description).exists()
		return resumes, exists
	
	@staticmethod
	def save_(profile, short_description, full_description, visible):
		try:
			resume = Resume.objects.get(profile=profile)
			resume.short_description = short_description
			resume.full_description = full_description
			resume.visible = visible
			resume.save()
		except Resume.DoesNotExist:
			resume = Resume()
			resume.profile = profile
			resume.short_description = short_description
			resume.full_description = full_description
			resume.visible = visible
			resume.save()

	file = models.FileField(
		null=True,
		upload_to=lambda instance, filename: 
			colabre.settings.UPLOAD_DIR
			+ '/resumes/'
			+ str(instance.id)
			+ '/' 
			+ filename
		)

	def __unicode__(self):
		return self.short_description

class Segment(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)

	@classmethod
	def getAllActive(cls):
		cursor = connection.cursor()
		cursor.execute(
			"""			
			select  
				jt.id							, 
			 	jt.id 		as job_title_id		, 
			 	jt.name		as job_title_name	, 
			 	se.id 		as segment_id 		, 
				se.name		as segment_name		
			 from colabre_web_jobtitle jt 
			 	inner join colabre_web_segment se	on jt.segment_id = se.id 
			 	inner join colabre_web_job jo		on jo.job_title_id = jt.id 
			 where jt.active = 1 
			 	and jo.active = 1 
			 	and se.active = 1
			 group by 
			 	jt.id		,
			 	jt.name		,
			 	se.id 	 	,
				se.name	
			 order by
			 	se.name	,
			 	jt.name	; """
		)
		all = dictfetchall(cursor)
		segments = []
		[{
			'id' : s['segment_id'],
			'name' : s['segment_name'],
		} for s in all
			if 
			{
				'id' : s['segment_id'],
				'name' : s['segment_name'],
			} not in segments 
			and segments.append({
				'id' : s['segment_id'],
				'name' : s['segment_name'],
			})]
		job_titles = []
		[{
			'id' : j['job_title_id'],
			'name' : j['job_title_name'],
			'segment_id' : j['segment_id']
		} for j in all
			if 
			{
				'id' : j['job_title_id'],
				'name' : j['job_title_name'],
				'segment_id' : j['segment_id']
			} not in job_titles
			and job_titles.append({
				'id' : j['job_title_id'],
				'name' : j['job_title_name'],
				'segment_id' : j['segment_id']
			})]
		for segment in segments:
			segment['job_titles'] = [job_title for job_title in job_titles if segment['id'] == job_title['segment_id']]

		return segments
		
	@classmethod
	def getAllActiveByProfile(cls, profile):
		cursor = connection.cursor()
		cursor.execute(
			"""			
			select  
				jt.id							, 
			 	jt.id 		as job_title_id		, 
			 	jt.name		as job_title_name	, 
			 	se.id 		as segment_id 		, 
				se.name		as segment_name		
			 from colabre_web_jobtitle jt 
			 	inner join colabre_web_segment se	on jt.segment_id = se.id 
			 	inner join colabre_web_job jo		on jo.job_title_id = jt.id 
			 where jt.active = 1 
			 	and jo.active = 1 
			 	and se.active = 1
			 	and jo.profile_id = {0}
			 group by 
			 	jt.id		,
			 	jt.name		,
			 	se.id 	 	,
				se.name	
			 order by
			 	se.name	,
			 	jt.name	; 
			""".format(profile.id)
		)
		all = dictfetchall(cursor)
		segments = []
		[{
			'id' : s['segment_id'],
			'name' : s['segment_name'],
		} for s in all
			if 
			{
				'id' : s['segment_id'],
				'name' : s['segment_name'],
			} not in segments 
			and segments.append({
				'id' : s['segment_id'],
				'name' : s['segment_name'],
			})]
		job_titles = []
		[{
			'id' : j['job_title_id'],
			'name' : j['job_title_name'],
			'segment_id' : j['segment_id']
		} for j in all
			if 
			{
				'id' : j['job_title_id'],
				'name' : j['job_title_name'],
				'segment_id' : j['segment_id']
			} not in job_titles
			and job_titles.append({
				'id' : j['job_title_id'],
				'name' : j['job_title_name'],
				'segment_id' : j['segment_id']
			})]
		for segment in segments:
			segment['job_titles'] = [job_title for job_title in job_titles if segment['id'] == job_title['segment_id']]

		return segments
	
	def __unicode__(self):
		return self.name

class JobTitle(models.Model):
	name = models.CharField(max_length=50)
	segment = models.ForeignKey(Segment)
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s (%s)" % (self.name, self.segment.name)
		
class Company(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return self.name

class PoliticalLocation(models.Model):
	country_id = models.IntegerField()
	country_code = models.CharField(max_length=3)
	country_name = models.CharField(max_length=60)
	
	region_id = models.IntegerField()
	region_code = models.CharField(max_length=2)
	region_name = models.CharField(max_length=60)
	
	city_id = models.IntegerField(unique=True)
	city_name = models.CharField(max_length=60)
	
	active = models.BooleanField(default=True)
	
	@classmethod
	def getAllActiveCountries(cls):
		cursor = connection.cursor()
		cursor.execute(
			"""
			select l.* 
			from colabre_web_politicallocation l 
				inner join colabre_web_job j on j.workplace_political_location_id = l.id
			where j.active = 1
			order by 
				l.country_code, 
				l.region_code, 
				l.city_name 
			"""
		)
		locations = dictfetchall(cursor)
		countries = []
		[{
			'id' : c['country_id'],
			'code' : c['country_code'],
			'name' : c['country_name'],
		} for c in locations
			if 
			{
				'id' : c['country_id'],
				'code' : c['country_code'],
				'name' : c['country_name'],
			} not in countries 
			and countries.append({
				'id' : c['country_id'],
				'code' : c['country_code'],
				'name' : c['country_name'],
				})]
					
		regions = []
		[{
			'id' : r['region_id'],
			'country_id' : r['country_id'],
			'code' : r['region_code'],
			'name' : r['region_name'],
		} for r in locations
			if 
			{
				'id' : r['region_id'],
				'country_id' : r['country_id'],
				'code' : r['region_code'],
				'name' : r['region_name'],
			} not in regions 
			and regions.append({
				'id' : r['region_id'],
				'country_id' : r['country_id'],
				'code' : r['region_code'],
				'name' : r['region_name'],
				})]
				
		cities = []
		[{
			'id' : c['id'],
			'country_id' : c['country_id'],
			'region_id' : c['region_id'],
			'country_code' : c['country_code'],
			'region_code' : c['region_code'],
			'name' : c['city_name'],
			'friendly_name' : str(c),
		} for c in locations
			if 
			{
				'id' : c['id'],
				'country_id' : c['country_id'],
				'region_id' : c['region_id'],
				'country_code' : c['country_code'],
				'region_code' : c['region_code'],
				'name' : c['city_name'],
				'friendly_name' : str(c),
			} not in cities 
			and cities.append({
				'id' : c['id'],
				'country_id' : c['country_id'],
				'region_id' : c['region_id'],
				'country_code' : c['country_code'],
				'region_code' : c['region_code'],
				'name' : c['city_name'],
				'friendly_name' : str(c),
				})]

		for country in countries:
			country['regions'] = [region for region in regions if country['id'] == region['country_id']]
			for region in country['regions']:
				region['cities'] = [city for city in cities if city['country_id'] == region['country_id'] and city['region_id'] == region['id']]
				
		return countries
		
	@classmethod
	def getAllActiveCountriesByProfile(cls, profile):
		cursor = connection.cursor()
		cursor.execute(
			"""
			select l.* 
			from colabre_web_politicallocation l 
				inner join colabre_web_job j on j.workplace_political_location_id = l.id
			where j.active = 1
				and j.profile_id = {0}
			order by 
				l.country_code, 
				l.region_code, 
				l.city_name 
			""".format(profile.id)
		)
		locations = dictfetchall(cursor)
		countries = []
		[{
			'id' : c['country_id'],
			'code' : c['country_code'],
			'name' : c['country_name'],
		} for c in locations
			if 
			{
				'id' : c['country_id'],
				'code' : c['country_code'],
				'name' : c['country_name'],
			} not in countries 
			and countries.append({
				'id' : c['country_id'],
				'code' : c['country_code'],
				'name' : c['country_name'],
				})]
					
		regions = []
		[{
			'id' : r['region_id'],
			'country_id' : r['country_id'],
			'code' : r['region_code'],
			'name' : r['region_name'],
		} for r in locations
			if 
			{
				'id' : r['region_id'],
				'country_id' : r['country_id'],
				'code' : r['region_code'],
				'name' : r['region_name'],
			} not in regions 
			and regions.append({
				'id' : r['region_id'],
				'country_id' : r['country_id'],
				'code' : r['region_code'],
				'name' : r['region_name'],
				})]
				
		cities = []
		[{
			'id' : c['id'],
			'country_id' : c['country_id'],
			'region_id' : c['region_id'],
			'country_code' : c['country_code'],
			'region_code' : c['region_code'],
			'name' : c['city_name'],
			'friendly_name' : str(c),
		} for c in locations
			if 
			{
				'id' : c['id'],
				'country_id' : c['country_id'],
				'region_id' : c['region_id'],
				'country_code' : c['country_code'],
				'region_code' : c['region_code'],
				'name' : c['city_name'],
				'friendly_name' : str(c),
			} not in cities 
			and cities.append({
				'id' : c['id'],
				'country_id' : c['country_id'],
				'region_id' : c['region_id'],
				'country_code' : c['country_code'],
				'region_code' : c['region_code'],
				'name' : c['city_name'],
				'friendly_name' : str(c),
				})]

		for country in countries:
			country['regions'] = [region for region in regions if country['id'] == region['country_id']]
			for region in country['regions']:
				region['cities'] = [city for city in cities if city['country_id'] == region['country_id'] and city['region_id'] == region['id']]
				
		return countries
	
	def name(self):
		return self.__unicode__()
	
	def __unicode__(self):
		return "%s / %s / %s" % (self.city_name, self.region_code, self.country_code)
	
class Job(models.Model):

	def get_is_editable(self):
		now = time.mktime(datetime.now().timetuple())
		creation_date = time.mktime(self.creation_date.timetuple())
		return (int(now - creation_date) / 60) / 60 < 24
		
	is_editable = property(get_is_editable)

	profile = models.ForeignKey(UserProfile)
	
	segment_name = models.CharField(max_length=50)
	job_title = models.ForeignKey(JobTitle, null=True)
	job_title_name = models.CharField(max_length=50)
	
	workplace_political_location = models.ForeignKey(PoliticalLocation, null=True)
	workplace_political_location_name = models.CharField(max_length=120, null=True)
	workplace_location = models.CharField(max_length=120, null=True)
	
	description = models.TextField(max_length=5000)
	
	company = models.ForeignKey(Company, null=True)
	company_name = models.CharField(max_length=50, null=True)

	contact_email = models.EmailField(max_length=254, null=True)
	contact_phone = models.CharField(max_length=25, null=True)
	contact_name = models.CharField(max_length=61, null=True)
	
	creation_date = models.DateTimeField(default=datetime.now())
	published = models.BooleanField(default=True)
	
	active = models.BooleanField(default=True)

	# to remove
	@staticmethod
	def _view_search_my_jobs(profile, after_id, q, limit):
		query_id = Q(id__lt=after_id)
		if after_id == '0' or after_id == 0:
			query_id = Q()
			
		query_name = Q(
			Q(job_title_name__icontains=q) | 
			Q(description__icontains=q) |
			Q(segment_name__icontains=q) |
			Q(company_name__icontains=q)
		)
		if q == None:
			query_name = Q()
		
		jobs = Job.objects.filter(Q(profile=profile), query_id, query_name).order_by("-id")[:limit]
		exists = Job.objects.filter(Q(profile=profile), query_name).exists()
		return jobs, exists

	@staticmethod
	def view_search_my_jobs(profile, term, job_titles_ids, locations_ids, days, page, limit):
		
		query = Q(published=True) & Q(profile=profile)
		
		if days > 0:
			now = datetime.now()
			ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
			query = query & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if locations_ids:
			query = query & Q(workplace_political_location__in=(locations_ids))
		
		list = Job.objects.filter(
			Q(Q(description__icontains=term) | Q(job_title__name__icontains=term)), 
			query
		).order_by("-creation_date")

		jobs = None
		
		try:
			paginator = Paginator(list, limit)
			jobs = paginator.page(page)
		except EmptyPage:
			pass
		
		is_last_page = page >= paginator.num_pages
		total_jobs = paginator.count

		return jobs, is_last_page, total_jobs
		
	@staticmethod
	def view_search_public(term, job_titles_ids, locations_ids, days, page, limit):
		now = datetime.now()
		ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
		
		query = Q(published=True) & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if locations_ids:
			query = query & Q(workplace_political_location__in=(locations_ids))
		
		list = Job.objects.filter(
			Q(Q(description__icontains=term) | Q(job_title__name__icontains=term)), 
			query
		).order_by("-creation_date")

		jobs = None
		
		try:
			paginator = Paginator(list, limit)
			jobs = paginator.page(page)
		except EmptyPage:
			pass
		
		is_last_page = page >= paginator.num_pages
		total_jobs = paginator.count

		#print >> sys.stderr, "page: %r" % page
		return jobs, is_last_page, total_jobs
		
	def save(self, *args, **kwargs):
		
		job_title = None
		try:
			# segment and jobtitle exist, none created
			job_title = JobTitle.objects.get(name=self.job_title_name.strip(), segment__name=self.segment_name.strip())
		except:
			try:
				# only segment exists, job_title created
				segment = Segment.objects.get(name=self.segment_name.strip())
				job_title = JobTitle(name=self.job_title_name, segment=segment)
				job_title.save()
			except:
				# none exists, both created
				segment = Segment(name=self.segment_name)
				segment.save()
				job_title = JobTitle(name=self.job_title_name, segment=segment)
				job_title.save()
		self.job_title = job_title
		self.job_title_name = job_title.name
		self.segment_name = self.job_title.segment.name


		try:
			# IMPORTANT! check PoliticalLocation.name for correct format...
			location = self.workplace_political_location_name.split('/')
			city_name = location[0].strip()
			region_code = location[1].strip()
			country_code = location[2].strip()
			self.workplace_political_location = PoliticalLocation.objects.get(city_name=city_name, region_code=region_code, country_code=country_code)
		except:
			self.workplace_political_location = None
			
		try:
			self.company = Company.objects.get(name=self.company_name.strip())
			self.company_name = self.company.name
		except:
			company = Company(name=self.company_name)
			company.save()
			self.company = company
			self.company_name = company.name

		super(Job, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.title
	
class UserProfileVerification(models.Model):

	profile = models.ForeignKey(UserProfile, unique=True)
	uuid = models.CharField(max_length=36, default= lambda: str(uuid.uuid4()), unique=True)
	date_verified = models.DateTimeField(null=True)
	
	def __unicode__(self):
		return self.profile.__unicode__()
	
	def __setVerified(self, uuid):
		if uuid == self.uuid:
			if self.profile.is_verified:
				raise BusinessException("Usuário já verificado")
			self.date_verified = datetime.now()
			self.profile.is_verified = True
			self.save()
			self.profile.save()
			return True
		else:
			return False
	
	@staticmethod
	def create(profile):
		""" Create the user verification object.
			This whole thing of notification should be placed elsewhere
			since it will be very little used """
		verification = UserProfileVerification()
		verification.profile = profile
		verification.save()
		
		UserNotification.getNotification().notify(profile, verification.uuid)
		
		return verification
	
	@staticmethod
	def verify(uuid):
		verification = UserProfileVerification.objects.filter(uuid = uuid)[0]
		if verification is None:
			raise BusinessException(u"Número de verificação inexistente")
		verification.__setVerified(uuid)
		return verification.profile
		
	@staticmethod
	def resend_verification_email(user):
		profile = UserProfile.objects.get(user=user)
		verification = UserProfileVerification.objects.get(profile=profile)
		UserNotification.getNotification().notify(profile, verification.uuid)
