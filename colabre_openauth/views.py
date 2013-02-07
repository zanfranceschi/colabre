from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout as auth_logout
from django.contrib.messages.api import get_messages
from django.conf.urls import patterns, include, url
import social_auth
#from colabre_web.models import 

#from colabre_openauth.views import done, login_success, error

from django.conf.urls import patterns, include, url

urlpatterns = patterns('colabre_openauth.views',
	url(r'^error/$', 'error', name='error'),
	# We'll set up social_auth to send users here the first time they log in.
	# This can be set to your existing "welcome" page if you have one.
	url(r'^talent/new/$', 'done', name='new_account'),
	# This is where users will land after logging in through linkedin
	# once they've created an account. You can set it to your existing profile
	# page
	#url(r'^accounts/profile_/$', 'login_success', name='linkedin_login_success'),
	
	url(r'^XXXX', 'show_prospect', name='show_prospect'),
)

#from talent.models import Prospect

@login_required
def done(request):
	"""
	User has linked account successfully. This view is called after a new user
	signs up through Linkedin.
	"""
	details = request.user.social_auth.get().extra_data
	return HttpResponseRedirect(reverse('show_prospect', kwargs={'id': 'X'}))



#@login_required
#def login_success(request):
#	"""
#	Shows a prospect's profile page after a successful linkedin login.
#	"""
#	return HttpResponseRedirect(reverse(
#		# show_prospect is the url name for our profile page
#		'show_prospect',
#		kwargs={
#			'id': 'X'#request.user.account.prospect.id
#			}))


def error(request):
	"""Error view"""
	messages = get_messages(request)
	return render_to_response('base.html', {'messages': messages},
							  RequestContext(request))

							  
def show_prospect(request):
	return redirect('/')
							  
# def logout(request):
#	 """Logs out user"""
#	 auth_logout(request)
#	 return HttpResponseRedirect('/')

# def home(request):
#	 """Home view, displays login mechanism"""
#	 if request.user.is_authenticated():
#		 return HttpResponseRedirect(reverse('done'))
#	 else:
#		 return render_to_response('home.html',
#								   RequestContext(request))