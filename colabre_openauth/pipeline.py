from django.contrib.auth.models import User
from django.shortcuts import redirect
from colabre_web.models import UserProfile
import sys
from colabre.settings_linkedin import SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_URL

def check_oauth_email_existence(request, *args, **kwargs):
	pass
	"""
	details = kwargs.get('details')
	email = details['email']
	exists = User.objects.filter(email=email).count() > 0
	if (exists):
		return redirect(SOCIAL_AUTH_EMAIL_ALREAY_EXISTS_URL)
	"""

def bind_to_profile(request, *args, **kwargs):
	user = None
	if kwargs.get('user'):
		user = kwargs['user']
		print >> sys.stderr, "user", user
	else:
		username = request.session.get('saved_username')
		user = User.objects.get(username=username)
		print >> sys.stderr, "username", username
	
	test_profile = UserProfile.objects.filter(user=user)
	print >> sys.stderr, "kwargs", kwargs
	if user and not test_profile:
		print >> sys.stderr, "\n\n\nentrou em : if user and not test_profile:\n\n\n"
		profile = UserProfile()
		profile.user = user
		profile.is_verified = True
		profile.save()
		