from django.contrib.auth.models import User
from colabre_web.models import UserProfile
import sys

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
	
	if user and not test_profile:
		profile = UserProfile()
		profile.user = user
		profile.is_verified = True
		profile.save()