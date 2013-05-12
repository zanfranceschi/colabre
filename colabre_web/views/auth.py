from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from colabre_web.models import *
from colabre_web.forms import *
from helpers import *
from colabre.settings import EMAIL_SUPPORT

def get_template_path(template):
	return 'auth/%s' % template


def login_(request):
	if request.user.is_authenticated():
		return render(request, 'index.html')
	form = LoginForm()
	if request.GET.__contains__('next'):
		next = request.GET['next']
		form = LoginForm(initial={'next' : next})
	return render(request, get_template_path('login.html'), { 'form' : form })


def authenticate_(request):	
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			next = form.cleaned_data['next']
			user = authenticate(username=username, password=password)
			if user is not None:
				if not user.is_active:
					messages.error(request, u'Esta conta está inativa. Por favor, entre em contato com {0} e explique-nos seu problema.'.format(EMAIL_SUPPORT))
				else:
					login(request, user)
					try:
						return redirect(next)
					except:
						return redirect('/')
			else:
				messages.error(request, u'A combinação usuário/senha que você forneceu não existe.')
				return render(
					request, 
					get_template_path('login.html'), {'form' : form})
	else:
		form = LoginForm()
	return render(request, get_template_path('login.html'), {'form' : form})

@login_required
def logout_(request):
	logout(request)
	return redirect('/')