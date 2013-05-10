# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import render
from colabre_web.models import UserProfile, UserProfileVerification
from datetime import datetime
from colabre_web.oauth.settings import SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_TEMPLATE_PATH
import traceback
import logging
from django.contrib import messages
from colabre.settings import EMAIL_SUPPORT

def check_oauth_email_existence(request, *args, **kwargs):
	pass
	"""
	details = kwargs.get('details')
	email = details['email']
	username = details['username']
	exists = User.objects.filter(email=email).exclude(username=username).count() > 0
	try:
		if (exists):
			return render(request, SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_TEMPLATE_PATH, { 'email': email})
	except Exception:
		logging.error(traceback.format_exc())
	"""

def check_if_user_is_active(request, *args, **kwargs):
	user = None
	if kwargs.get('user'):
		user = kwargs['user']
	else:
		username = request.session.get('saved_username')
		user = User.objects.get(username=username)
	
	if (not user.is_active):
		messages.error(request, u"Seu usuário está inativado. Por favor, entre em contato com {0} nos explicando seu problema.".format(EMAIL_SUPPORT))
		return render(request, "home/index.html")

def bind_to_profile(request, *args, **kwargs):
	try:
		user = None
		if kwargs.get('user'):
			user = kwargs['user']
		else:
			username = request.session.get('saved_username')
			user = User.objects.get(username=username)
		
		data = {}
		if kwargs.get('response'):
			response = kwargs['response']
			if response.has_key('date-of-birth'):
				date = response['date-of-birth']
				
				if date.has_key('year'):
					data.update({'year' : date['year']})
			
				if date.has_key('month'):
					data.update({'month' : date['month']})
					
				if date.has_key('day'):
					data.update({'day' : date['day']})
			
			#if response.has_key('industry'):
			#	data.update({'resume_segment_name' : response['industry']})
				
			if response.has_key('summary'):
				data.update({'resume_short_description' : response['summary']})
					
		UserProfile.create_oauth_if_new(user, **data)
		
	except:
		logging.error(traceback.format_exc())
		
		