import time
from datetime import *
from django.db import models
from django.contrib.auth.models import User
#from django.template.defaultfilters import slugify
#from tastypie.utils import now
#from django_mongodb_engine.contrib import MongoDBManager
#from djangotoolbox.fields import *

class ColabreUser(models.Model):
	user = models.ForeignKey(User, unique=True)
	
	def __unicode__(self):
		return self.user.username


class Company(models.Model):
	name = models.CharField(max_length=75)
	field = models.CharField(max_length=75)

	#objects = MongoDBManager()
	
	def __unicode__(self):
		return self.name


class Job(models.Model):
	company = models.ForeignKey(Company)
	publisher = models.ForeignKey(ColabreUser, unique=True)
	
	title = models.CharField(max_length=75)
	description = models.TextField()
	published_at = models.DateTimeField()

	field = models.CharField(max_length=75)
	country = models.CharField(max_length=75)
	state = models.CharField(max_length=75)
	city = models.CharField(max_length=75)

	show_company = models.BooleanField()
	wage_description = models.CharField(max_length=75)

	#objects = MongoDBManager()

	'''
	def search(_from, _to, term, start, limit):
		return Job.objects.raw_query(
			{"$where" : 
			"(this.title + ' ' + this.description + ' ' + this.field).match(/{0}/gim) && (this.published_at >= new ISODate('{1}:00:00') && this.published_at <= new ISODate('{2}:23:59:59'))".format(term.replace(".", "\."), _from, _to)}
			).order_by("-published_at")[start:limit]
	'''

	def __unicode__(self):
		return self.title


class Resume(models.Model):
	publisher = models.ForeignKey(ColabreUser, unique=True)
	description = models.TextField()
	file = models.FileField(upload_to="/")
	updated_at = models.DateTimeField(auto_now = True, auto_now_add = True)
	
	def __unicode__(self):
		return self.publisher.user.username
