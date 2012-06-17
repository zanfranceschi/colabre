from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from main.models import *
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic.date_based import object_detail
from django.contrib.auth.decorators import login_required
from datetime import *
from django.db.models import Q
from django.db import connection
from django.utils.encoding import smart_unicode, smart_str
from django.utils.http import urlquote
import uuid
from django.core.mail import send_mail
from socket import gethostname
import time

def test(request):
	time.sleep(3)
	return HttpResponse("false")

def verify_registration(request, uuid):
	try:
		verification = ColabreUserVerification.objects.filter(uuid = uuid)[0]
		if verification is None:
			return register(request)
		
		verification.setVerified(uuid)
		
		user = authenticate(username=verification.user.user.username, password=verification.user.user.password)
		
		if user is not None:
			login(request, user)
			return render(request, 'index.html')
		
		return render(request, 'register.html')
	except BusinessException as be:
		return HttpResponse("Ocorreu um erro: %s" % be.message)

def register(request):
	return render(request, 'register.html')
	
def register_submit(request):
	if not request.POST:
		return register(request)
	else:
		# register new user!
		new_user = User()
		
		username = request.POST["username"]
		email = request.POST["email"]
		password = request.POST["password"]
		
		new_user.is_superuser = False
		new_user.is_staff = False
		new_user.is_active = True
		new_user.username = new_user.first_name = username
		new_user.email = email
		new_user.set_password(password)
		new_user.save()

		new_colabre_user = ColabreUser()
		new_colabre_user.user = new_user
		new_colabre_user.save()
		
		verification = ColabreUserVerification()
		verification.user = new_colabre_user
		verification.save()
		
		user = authenticate(username=new_user.username, password=password)
		
		if user is not None:
			login(request, user)
		
			send_mail(
				'Colabre | Registro', 
'''Parabéns, %(name)s e obrigado por ter se registrado no Colabre!

Por favor, confirme seu registro acessando o link a seguir:
http://127.0.0.1:8000/registrar/verificar/%(uuid)s

Equipe Colabre.org''' % {"name": new_user.first_name, "uuid": verification.uuid},
				'no-reply@colabre.org', 
				[new_user.email], 
				fail_silently=False)

			return render(
				request, 
				'register.html', 
				{
					'signedup': True,
					'new_user' : new_user
				})

def login_view(request):
	return render(request, 'login.html')
	
def autenticar(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)

	data = { 'message': None }
	
	if user is not None:
		if user.is_active:
			login(request, user)
			data = { 'message': 'Ok.' }
		else:
			data = { 'message': 'Sua conta está desabilitada.' }
	else:
		data = { 'message': 'Combinação usuário/senha inválida.' }
	
	return render(request, 'login.html', data)

#@login_required
def logout_view(request):
	logout(request)
	return render(request, 'login.html', { 'message' : 'Usuário deslogado.' })

