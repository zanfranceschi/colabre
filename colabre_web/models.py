# -*- coding: UTF-8 -*-
from aux_models import *
from django.db import models, connection
from django.db.models import Q
from django.core.exceptions import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import authenticate
from django.template import Context
import uuid
from datetime import *
import time
import colabre.settings
import sys

def dictfetchall(cursor):
	"Returns all rows from a cursor as a dict"
	desc = cursor.description
	return [
		dict(zip([col[0] for col in desc], row))
		for row in cursor.fetchall()
	]


class Country(models.Model):
	name = models.CharField(max_length=60)
	code = models.CharField(max_length=3, null=True)
	
	def __unicode__(self):
		return self.name
	
	@classmethod
	def get_full_countries_by_sql_query(cls, sql_query):
		"""
		 Expected columns projection:
			country_id
			country_code
			country_name
			region_id
			region_code
			region_name
			city_id
			city_name
		"""
		cursor = connection.cursor()
		cursor.execute(sql_query)
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
				'id' : c['city_id'],
				'country_id' : c['country_id'],
				'region_id' : c['region_id'],
				'country_code' : c['country_code'],
				'region_code' : c['region_code'],
				'name' : c['city_name'],
				'friendly_name' : str(c),
			} not in cities 
			and cities.append({
				'id' : c['city_id'],
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
	
class Region(models.Model):
	name = models.CharField(max_length=60)
	code = models.CharField(max_length=2, null=True)
	country = models.ForeignKey(Country)
	
	def __unicode__(self):
		return self.code if self.code else self.name
	
class City(models.Model):
	name = models.CharField(max_length=60)
	region = models.ForeignKey(Region)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.name
	
	def full_name(self):
		return "%s / %s / %s" % (self.name, self.region, self.region.country)
	
	@classmethod
	def get_existing_or_create(cls, country_name, region_name, city_name):
		countries = Country.objects.filter(name=country_name)
		country = countries[0] if countries else None
		if not country:
			country = Country()
			country.name = country_name
			country.save()
			
		regions = Region.objects.filter(Q(country=country) & Q(Q(name=region_name) | Q(code=region_name)))
		region = regions[0] if regions else None
		if not region:
			region = Region()
			region.name = region_name
			if len(region_name.strip()) == 2:
				region.code = region_name.strip().upper()
			region.country = country
			region.save()
			
		cities = City.objects.filter(Q(region__country=country) & Q(Q(region__name=region_name) | Q(region__code=region_name)) & Q(name=city_name))
		city = cities[0] if cities else None
		if not city:
			city = City()
			city.name = city_name
			city.region = region
			city.save() 
		
		return city
	
class UserProfile(models.Model):
	""" 
		Binds Django user to resume and jobs
	"""
	#company = models.ForeignKey('domain.Company')
	user = models.ForeignKey(User, unique=True)
	is_verified = models.BooleanField(default=False)
	is_from_oauth = models.BooleanField(default=False)
	profile_type = models.CharField(max_length=2, choices=(('JS', 'Buscar Vagas'), ('JP', 'Publicar Vagas')))
	gender = models.CharField(default='U', max_length=1, choices=(('U', 'Indefinido'), ('F', 'Feminino'), ('M', 'Masculino')))
	birthday = models.DateField(null=True)
	city = models.ForeignKey(City, null=True)
	excluded = models.BooleanField(default=False)
	active = models.BooleanField(default=True)
	
	def set_password(self, password):
		self.user.set_password(password)
		self.user.save()

	@classmethod
	def retrieve_access(cls, username_or_email):
		profiles = UserProfile.objects.filter(Q(user__username=username_or_email) | Q(user__email=username_or_email)).exclude(is_from_oauth=True)
		for user in [profile.user for profile in profiles]:
			um = UserManager()
			new_password = um.make_random_password(6, user.username)
			user.set_password(new_password)
			user.save()
			UserNotification.getNotification().notify_password_change(user, new_password)
		return len(profiles) > 0

	@classmethod
	def get_profile_by_user(cls, user):
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
	
	@classmethod
	def create(cls, username, email, password):
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
	
	@classmethod
	def create_oauth_if_new(cls, user, **kwargs):
		should_not_exist_profile = cls.objects.filter(user=user)
		if (user and not should_not_exist_profile):
			profile = UserProfile()
			profile.user = user
			profile.is_verified = True
			profile.is_from_oauth = True
			if kwargs.get('year') and kwargs.get('month') and kwargs.get('day'):
				profile.birthday = datetime(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
			
			profile.save()
			
			resume_segment_name = ' '
			resume_short_description = ' '
			should_save = False
			
			if kwargs.get('resume_segment_name'):
				resume_segment_name = kwargs['resume_segment_name']
				should_save = True
			
			if kwargs.get('resume_short_description'):
				resume_short_description = kwargs['resume_short_description'][0:255]
				should_save = True
			
			if should_save:	
				Resume.save_(profile, resume_segment_name, resume_short_description, '', False)
		
	@classmethod
	def update_profile(
					cls,
					user, 
					first_name, 
					last_name, 
					email, 
					profile_type, 
					gender,
					birthday,
					country,
					region,
					city):
		profile = cls.objects.get(user=user)
		profile.user.first_name = first_name
		profile.user.last_name = last_name
	
		new_email = email
		if new_email.lower() != profile.user.email.lower() and profile.is_verified:
			verification = UserProfileVerification.objects.get(profile=profile)
			verification.uuid = str(uuid.uuid4())
			verification.save()
			UserNotification.getNotification().notify(profile, verification.uuid)
			profile.is_verified = False
		profile.user.email = email
	
		profile.profile_type = profile_type
		profile.gender = gender
		profile.birthday = birthday
		profile.city = City.get_existing_or_create(country, region, city)
		profile.save()

	@classmethod
	def update_profile_oauth(
							cls,
							user, 
							profile_type, 
							gender,
							birthday,
							country,
							region, 
							city):
		profile = cls.objects.get(user=user)
		profile.profile_type = profile_type
		profile.gender = gender
		profile.birthday = birthday
		profile.city = City.get_existing_or_create(country, region, city)
		profile.save()

	def save(self, *args, **kwargs):
		user = User.objects.get(id=self.user.id)
		if user.email != self.user.email:
			self.is_verified = False
		super(UserProfile, self).save(*args, **kwargs)
		self.user.save()
		
	@classmethod
	def get_countries_for_search_filter(cls, profile):
		query = """select
					co.id		country_id		,	
					co.code		country_code	,	
					co.name		country_name	,
					r.id		region_id		,
					r.code		region_code		,
					r.name		region_name		,
					ci.id		city_id			,
					ci.name		city_name
				from colabre_web_country co
					inner join colabre_web_region r on co.id = r.country_id
					inner join colabre_web_city ci	on r.id = ci.region_id
					inner join colabre_web_job j	on ci.id = j.city_id
				where j.active = 1
					and ci.active = 1
					and j.profile_id = {0}
				order by
					co.name,
					r.name,
					ci.name """.format(profile.id)
		return Country.get_full_countries_by_sql_query(query)
	
	@classmethod
	def get_segments_for_search_filter(cls, profile):
		query = """			
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
		return Segment.get_segments_by_sql_query(query)

class Segment(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)

	@classmethod
	def get_existing_or_create(cls, segment_name):
		segments = Segment.objects.filter(name=segment_name.strip())[:1]
		segment = segments[0] if segments else None
		if not segment:
			segment = Segment()
			segment.name = segment_name.strip()
			segment.save()

		return segment

	@classmethod
	def get_segments_by_sql_query(cls, sql_query):
		cursor = connection.cursor()
		cursor.execute(sql_query)
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
	
	@classmethod
	def get_existing_or_create(cls, segment_name, job_title_name):
		segment = Segment.get_existing_or_create(segment_name)
		
		job_titles = JobTitle.objects.filter(name=job_title_name.strip(), segment=segment)
		job_title = job_titles[0] if job_titles else None
		if not job_title:
			job_title = JobTitle()
			job_title.name = job_title_name.strip()
			job_title.segment = segment
			job_title.save()
		
		return job_title
	
	def __unicode__(self):
		return self.name
	
	def full_name(self):
		return "%s (%s)" % (self.name, self.segment.name)
		
class Company(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)
	
	@classmethod
	def get_existing_or_create(cls, company_name):
		companies = cls.objects.filter(name=company_name.strip())
		company = companies[0] if companies else None
		if not company:
			company = Company()
			company.name = company_name.strip()
			company.save()
		
		return company
	
	def __unicode__(self):
		return self.name

class Resume(models.Model):
	profile = models.ForeignKey(UserProfile, unique=True)
	
	segment_name = models.CharField(max_length=50)
	segment = models.ForeignKey(Segment, null=True)
	
	short_description = models.TextField(max_length=255)
	full_description = models.TextField()
	visible = models.BooleanField(default=True)
	active = models.BooleanField(default=True)
	created = models.DateField(auto_now_add=True)
	last_update = models.DateField(auto_now=True)
	
	def __unicode__(self):
		return u"%s - %s" % (self.profile, self.short_description[:32])
	
	def try_get_job_title(self, index):
		return self.segments[index-1:index]
	
	@classmethod
	def view_search_public(cls, term, segments_ids, cities_ids, page, limit):
		
		query = Q(visible=True)
		
		if segments_ids:
			query = query & Q(segment__in=(segments_ids))
			
		if cities_ids:
			query = query & Q(profile__city__in=(cities_ids))
		
		list = cls.objects.filter(
			Q(Q(short_description__icontains=term) | Q(full_description__icontains=term)), 
			query
		).select_related().order_by("-last_update")

		resumes = None
		
		try:
			paginator = Paginator(list, limit)
			resumes = paginator.page(page)
		except EmptyPage:
			pass
		
		is_last_page = page >= paginator.num_pages
		total_resumes = paginator.count
		return resumes, is_last_page, total_resumes
	
	@classmethod
	def save_(
			cls, 
			profile, 
			segment_name, 
			short_description, 
			full_description, 
			visible):
		objs = Resume.objects.filter(profile=profile)
		resume = objs[0] if objs else Resume() 
		resume.profile = profile
		resume.segment_name = segment_name
		resume.segment = Segment.get_existing_or_create(segment_name)
		resume.short_description = short_description
		resume.full_description = full_description
		resume.visible = visible
		resume.save()

	@classmethod
	def get_countries_for_search_filter(cls):
		query = """select
					co.id		country_id		,	
					co.code		country_code	,	
					co.name		country_name	,
					r.id		region_id		,
					r.code		region_code		,
					r.name		region_name		,
					ci.id		city_id			,
					ci.name		city_name
				from colabre_web_country co
					inner join colabre_web_region r 		on co.id = r.country_id
					inner join colabre_web_city ci			on r.id = ci.region_id
					inner join colabre_web_userprofile p	on ci.id = p.city_id 
					inner join colabre_web_resume re		on p.id = re.profile_id
				where re.active = 1 
					and re.visible = 1
					and p.active = 1
					and p.excluded = 0
				order by
					co.name,
					r.name,
					ci.name """ 
		return Country.get_full_countries_by_sql_query(query)
	
	@classmethod
	def get_segments_for_search_filter(cls):
		query = """
				select  
					0 			as id				, 
					0 			as job_title_id		, 
					'x'			as job_title_name	, 
					se.id 		as segment_id 		, 
					se.name		as segment_name		
				 from colabre_web_segment se
					inner join colabre_web_resume re on re.segment_id = se.id
				 where se.active = 1	
					and re.visible = 1 
				 group by 
					id					,
					job_title_id		,
					job_title_name 	 	,
					se.id				,
					se.name
				 order by
					se.name ;"""
		return Segment.get_segments_by_sql_query(query)

class Job(models.Model):

	def get_is_editable(self):
		now = time.mktime(datetime.now().timetuple())
		creation_date = time.mktime(self.creation_date.timetuple())
		return (int(now - creation_date) / 60) / 60 < 24
		
	is_editable = property(get_is_editable)

	profile = models.ForeignKey(UserProfile)
	job_title = models.ForeignKey(JobTitle)
	address = models.CharField(max_length=120, null=True)
	city = models.ForeignKey(City, null=True)
	description = models.TextField(max_length=5000)
	company = models.ForeignKey(Company, null=True)
	contact_name = models.CharField(max_length=60)
	contact_email = models.EmailField(max_length=254)
	contact_phone = models.CharField(max_length=25, null=True)
	creation_date = models.DateTimeField(auto_now_add=True)
	published = models.BooleanField(default=True)
	active = models.BooleanField(default=True)
	approved = models.BooleanField(default=False)
	uuid = models.CharField(max_length=36, default=lambda: str(uuid.uuid4()), null=True)
	approval_date = models.DateTimeField(null=True)

	segment_name = None 
	job_title_name = None
	country_name = None
	region_name = None
	city_name = None
	company_name = None

	def to_string(self):
		return u"""
user				{0}
segment				{1}
title				{2}
country				{3}
region				{4}
city				{5}
address				{6}
contact name		{7}
contact email		{8}
contact phone		{9}
description:
---
{10}
---

ver: {13}vagas/detalhar/{11}
aprovar: {13}colabre-admin/vaga/aprovar/{11}/{12}
""".format(
		self.profile.user.first_name,
		self.job_title.segment.name,
		self.job_title.name,
		self.city.region.country.name,
		self.city.region.name,
		self.city.name,
		self.address,
		self.contact_name,
		self.contact_email,
		self.contact_phone,
		self.description,
		self.id,
		self.uuid,
		colabre.settings.HOST_ROOT_URL
		)

	@classmethod
	def approve(cls, id, uuid):
		try:
			job_to_approve = Job.objects.get(id=id, uuid=uuid, approved=False)
			job_to_approve.save(**{'approve' : True})
			return job_to_approve
		except Job.DoesNotExist:
			return None

	def delete(self):
		self.active = False
		self.save()

	def save(self, *args, **kwargs):
		if (kwargs.pop('approve', False) == True or self.profile.user.username == 'colabre'):
			self.approved = True
			self.approval_date = datetime.now()
		else:
			self.uuid = str(uuid.uuid4())
			self.approved = False
			self.approval_date = None
			
		if self.job_title_name:
			self.job_title = JobTitle.get_existing_or_create(self.segment_name, self.job_title_name)
		
		if self.city_name and self.region_name and self.country_name:
			self.city = City.get_existing_or_create(self.country_name, self.region_name, self.city_name)
			
		if self.company_name:
			self.company = Company.get_existing_or_create(self.company_name)
		
		super(Job, self).save(*args, **kwargs)


	def __unicode__(self):
		return u"{0} - {1} ({2})".format(self.creation_date.date().strftime("%Y/%m/%d"), self.job_title.name, self.city)

	@classmethod
	def view_search_my_jobs(cls, profile, term, job_titles_ids, cities_ids, days, page, limit):
		
		query = Q(published=True) & Q(profile=profile)
		
		if days > 0:
			now = datetime.now()
			ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
			query = query & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if cities_ids:
			query = query & Q(city__in=(cities_ids))
		
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
		
	@classmethod
	def view_search_public(cls, term, job_titles_ids, cities_ids, days, page, limit):
		now = datetime.now()
		ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
		
		query = Q(approved=True) & Q(published=True) & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if cities_ids:
			query = query & Q(city__in=(cities_ids))
		
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
	
	
	@classmethod
	def get_countries_for_search_filter(cls):
		query = """select
					co.id		country_id		,	
					co.code		country_code	,	
					co.name		country_name	,
					r.id		region_id		,
					r.code		region_code		,
					r.name		region_name		,
					ci.id		city_id			,
					ci.name		city_name
				from colabre_web_country co
					inner join colabre_web_region r on co.id = r.country_id
					inner join colabre_web_city ci	on r.id = ci.region_id
					inner join colabre_web_job j	on ci.id = j.city_id
				where j.active = 1
					and j.approved = 1
				order by
					co.name,
					r.name,
					ci.name """ 
		return Country.get_full_countries_by_sql_query(query)
	
	@classmethod
	def get_segments_for_search_filter(cls):
		query = """			
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
				 	and jo.approved = 1
				 	and se.active = 1
				 group by 
				 	jt.id		,
				 	jt.name		,
				 	se.id 	 	,
					se.name	
				 order by
				 	se.name	,
				 	jt.name	; """
		return Segment.get_segments_by_sql_query(query)
		
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
	
	@classmethod
	def create(cls, profile):
		verification = UserProfileVerification()
		verification.profile = profile
		verification.save()
		
		UserNotification.getNotification().notify(profile, verification.uuid)
		
		return verification
	
	@classmethod
	def create_verified(cls, profile):
		verification = UserProfileVerification()
		verification.date_verified = datetime.now()
		verification.profile = profile
		verification.save()
		return verification
	
	@classmethod
	def verify(cls, uuid):
		verification = UserProfileVerification.objects.filter(uuid = uuid)[0]
		if verification is None:
			raise BusinessException(u"Número de verificação inexistente")
		verification.__setVerified(uuid)
		return verification.profile
		
	@classmethod
	def resend_verification_email(cls, user):
		profile = UserProfile.objects.get(user=user)
		verification = UserProfileVerification.objects.get(profile=profile)
		UserNotification.getNotification().notify(profile, verification.uuid)