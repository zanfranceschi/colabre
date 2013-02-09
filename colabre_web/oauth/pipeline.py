from django.contrib.auth.models import User
from django.shortcuts import render
from colabre_web.models import UserProfile, UserProfileVerification
import sys
from datetime import datetime
from colabre.settings_linkedin import SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_TEMPLATE_PATH

def check_oauth_email_existence(request, *args, **kwargs):
	print >> sys.stderr, "\n\n", kwargs, "\n\n"
	print >> sys.stderr, "\n\n", args, "\n\n"
	details = kwargs.get('details')
	email = details['email']
	username = details['username']
	exists = User.objects.filter(email=email).exclude(username=username).count() > 0
	try:
		if (exists):
			return render(request, SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_TEMPLATE_PATH, { 'email': email})
	except Exception, e:
		import traceback
		traceback.print_exc()

def bind_to_profile(request, *args, **kwargs):
	user = None
	if kwargs.get('user'):
		user = kwargs['user']
	else:
		username = request.session.get('saved_username')
		user = User.objects.get(username=username)
	
	test_profile = UserProfile.objects.filter(user=user)
	if user and not test_profile:
		profile = UserProfile()
		profile.user = user
		profile.is_verified = True
		profile.is_from_oauth = True
		if kwargs.get('response'):
			response = kwargs['response']
			if response.has_key('date-of-birth'):
				date = response['date-of-birth']
				if date.has_key('day') and date.has_key('month') and date.has_key('year'):
					profile.birthday = datetime(
											int(date['year']),
											int(date['month']),
											int(date['day']))
		profile.save()
		UserProfileVerification.create_verified(profile)
		