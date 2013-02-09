from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from colabre_web.models import *
from colabre_web.forms import *
from helpers import handle_exception

def get_template_path(template):
	return 'registration/%s' % template

@handle_exception
def index(request):
	if request.user.is_authenticated():
		return redirect("/")

	if request.method == 'POST': # If the form has been submitted...
		form = RegisterForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			new_profile = form.save()
			user = authenticate(username=new_profile.user.username, password=form.cleaned_data['password'])
			#print >> sys.stderr, user
			if user is not None:
				login(request, user)
				return render(request, get_template_path('thanks.html'))
	else:
		form = RegisterForm() # An unbound form
	return render(request, get_template_path('index.html'), {
		'form' : form,
		'submitted' : True
	})