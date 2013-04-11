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
	
class Region(models.Model):
	name = models.CharField(max_length=60)
	code = models.CharField(max_length=2, null=True)
	country = models.ForeignKey(Country)
	
	def __unicode__(self):
		return self.code if self.code is not None else self.name
	
class City(models.Model):
	name = models.CharField(max_length=60)
	region = models.ForeignKey(Region)
	
	def __unicode__(self):
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
	

	@classmethod
	def get_full_countries_by_sql_query(cls, sql_query):
		"""
		 Expected projection:
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
		

class Location(models.Model):
	country_id = models.AutoField()
	country = models.CharField(max_length=60)
	#country_code = models.CharField(max_length=3, null=True)
	region_id = models.AutoField()
	region = models.CharField(max_length=60)
	#region_code = models.CharField(max_length=2, null=True)
	city = models.CharField(max_length=60)
	active = models.BooleanField(default=True)
	
	@classmethod
	def try_parse(cls, country, region, city):
		try:
			query = Q(city=city) & Q(region=region) & Q(country=country) 
			return cls.objects.filter(query)[0]
		except:
			return None
	
	@classmethod
	def getCountriesByQuery(cls, query):
		cursor = connection.cursor()
		cursor.execute(query)
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
		return "%s / %s / %s" % (self.city, self.region, self.country)

class UserProfile(models.Model):
	""" Binds Django user to resume and jobs """
	#company = models.ForeignKey('domain.Company')
	user = models.ForeignKey(User, unique=True)
	is_verified = models.BooleanField(default=False)
	is_from_oauth = models.BooleanField(default=False)
	profile_type = models.CharField(max_length=2, choices=(('JS', 'Buscar Vagas'), ('JP', 'Publicar Vagas')))
	gender = models.CharField(default='U', max_length=1, choices=(('U', 'Indefinido'), ('F', 'Feminino'), ('M', 'Masculino')))
	birthday = models.DateField(null=True)
	
	#political_location = models.ForeignKey(PoliticalLocation, null=True)
	#political_location_name = models.CharField(max_length=120, null=True)
	
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
		return True

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
	def getCountriesForSearchFilter(cls, profile):
		query = """	select distinct l.* 
					from colabre_web_politicallocation l 
						inner join colabre_web_job j on j.location_id = l.id
					where j.active = 1
						and j.profile_id = {0}
					order by l.country_code, l.region_code, l.city_name """.format(profile.id)
		return PoliticalLocation.getCountriesByQuery(query)
	
	@classmethod
	def getSegmentsForSearchFilter(cls, profile):
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
		return Segment.getSegmentsByQuery(query)

class Segment(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)

	@classmethod
	def try_parse(cls, segment_name):
		objs = cls.objects.filter(name=segment_name)
		return objs[0] if objs else None

	@classmethod
	def getSegmentsByQuery(cls, query):
		cursor = connection.cursor()
		cursor.execute(query)
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
	def try_parse(cls, segment_name, job_title_name):
		objs = cls.objects.filter(segment__name=segment_name, name=job_title_name)
		return objs[0] if objs else None
		
	def __unicode__(self):
		return "%s (%s)" % (self.name, self.segment.name)
		
class Company(models.Model):
	name = models.CharField(max_length=50, unique=True)
	active = models.BooleanField(default=True)
	
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
	
	last_update = models.DateField(auto_now=True)
	
	def try_get_job_title(self, index):
		return self.segments[index-1:index]
	
	@classmethod
	def view_search_public(cls, term, segments_ids, locations_ids, page, limit):
		
		query = Q(visible=True)
		
		if segments_ids:
			query = query & Q(segment__in=(segments_ids))
			
		if locations_ids:
			query = query & Q(profile__political_location__in=(locations_ids))
		
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
		resume.segment = Segment.try_parse(segment_name)
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
	
	@classmethod
	def getCountriesForSearchFilter(cls):
		query = """	select distinct l.* 
					from colabre_web_politicallocation l 
						inner join colabre_web_userprofile up on up.political_location_id = l.id
					where up.active = 1
					order by l.country_code, l.region_code, l.city_name """
		return PoliticalLocation.getCountriesByQuery(query)
	
	@classmethod
	def getSegmentsForSearchFilter(cls):
		query = """
				select  
					jt.id							, 
					jt.id 		as job_title_id		, 
					jt.name		as job_title_name	, 
					se.id 		as segment_id 		, 
					se.name		as segment_name		
				 from colabre_web_jobtitle jt 
					inner join colabre_web_segment se	on jt.segment_id = se.id 
					inner join colabre_web_resume re	on re.segment_id = se.id
				 where jt.active = 1 
					and se.active = 1	
					and re.visible = 1 
				 group by 
					jt.id		,
					jt.name		,
					se.id 	 	,
					se.name	
				 order by
					se.name	,
					jt.name	;"""
		return Segment.getSegmentsByQuery(query)

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
	
	#workplace_political_location = models.ForeignKey(PoliticalLocation, null=True)
	#workplace_political_location_name = models.CharField(max_length=120, null=True)
	address = models.CharField(max_length=120, null=True)
	location = models.ForeignKey(PoliticalLocation, null=True)
	country = models.CharField(max_length=60)
	region = models.CharField(max_length=60)
	city = models.CharField(max_length=60)
	
	description = models.TextField(max_length=5000)
	
	company = models.ForeignKey(Company, null=True)
	company_name = models.CharField(max_length=50, null=True)

	contact_email = models.EmailField(max_length=254, null=True)
	contact_phone = models.CharField(max_length=25, null=True)
	contact_name = models.CharField(max_length=61, null=True)
	
	creation_date = models.DateTimeField(default=datetime.now())
	published = models.BooleanField(default=True)
	
	active = models.BooleanField(default=True)

	@classmethod
	def view_search_my_jobs(cls, profile, term, job_titles_ids, locations_ids, days, page, limit):
		
		query = Q(published=True) & Q(profile=profile)
		
		if days > 0:
			now = datetime.now()
			ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
			query = query & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if locations_ids:
			query = query & Q(location__in=(locations_ids))
		
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
	def view_search_public(cls, term, job_titles_ids, locations_ids, days, page, limit):
		now = datetime.now()
		ref_datetime = datetime(now.year, now.month, now.day) - timedelta(days=days)
		
		query = Q(published=True) & Q(creation_date__gte=ref_datetime)
		
		if job_titles_ids:
			query = query & Q(job_title__in=(job_titles_ids))
			
		if locations_ids:
			query = query & Q(location__in=(locations_ids))
		
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
		
		self.location = PoliticalLocation.try_parse(self.country, self.region, self.city)
		if self.location is not None:
			self.country = self.location.country_code 
			self.region = self.location.region_code
			self.city = self.location.city_name
		else:
			pass
		
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
		return self.job_title_name
	
	@classmethod
	def getCountriesForSearchFilter(cls):
		query = """	select distinct l.* 
					from colabre_web_politicallocation l 
						inner join colabre_web_job j on j.location_id = l.id
					where j.active = 1
					order by l.country_code, l.region_code, l.city_name """
		return PoliticalLocation.getCountriesByQuery(query)
	
	@classmethod
	def getSegmentsForSearchFilter(cls):
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
				 group by 
				 	jt.id		,
				 	jt.name		,
				 	se.id 	 	,
					se.name	
				 order by
				 	se.name	,
				 	jt.name	; """
		return Segment.getSegmentsByQuery(query)
		
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