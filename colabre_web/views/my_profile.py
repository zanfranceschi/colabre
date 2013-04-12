# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from colabre_web.models import *
from colabre_web.forms import *
from helpers import *
from django.conf.urls import patterns, url
from django.core.cache import cache

urlpatterns = patterns('colabre_web.views.my_profile',
	url(r'^$', 'index', name='my_profile_index'),
	url(r'^alterar-senha/$', 'change_password', name='my_profile_change_password'),
	url(r'^parcial/reenviar-email-verificacao/$', 'partial_resend_verification_email', name='my_profile_resend_verification_email'),
	url(r'^verificar-email/([\w\d\-]+)/$', 'verify_email', name='my_profile_verify_email'),
	url(r'^solicitar-verificacao/$', 'demand_verification', name='my_profile_demand_verification'),
	url(r'^recuperar-acesso/$', 'retrieve_access', name='my_profile_retrieve_access'),
)

def get_template_path(template):
	return 'my-profile/%s' % template

@login_required
def demand_verification(request):
	if request.user.get_profile().is_verified:
		return render(request, 'index.html')	
	return render(request, get_template_path('demand-verification.html'))
	
@login_required
def index(request):
	if request.method == 'POST':
		form = get_user_profile_form(request.POST, user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, 'Perfil atualizado.')
		else:
			messages.error(request, 'Verifique o preenchimento do perfil.')
	else:
		form = get_user_profile_form(user=request.user)
	return render(request, get_template_path('index.html'), {'form' : form })

@login_required
def partial_resend_verification_email(request):
	try:
		UserProfileVerification.resend_verification_email(request.user)
		return HttpResponse('1')
	except Exception:
		return HttpResponse('0')
	
def verify_email(request, uuid):
	try:
		profile = UserProfileVerification.verify(uuid)
		if profile:
			messages.success(request, 'Obrigado! Seu email foi verificado com sucesso.')
		if request.user:
			form = get_user_profile_form(user=request.user)
			return render(request, get_template_path('index.html'), {'form' : form})
	except Exception:
		pass
	return render(request, 'index.html')

@login_required
def change_password(request):
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST, user=request.user)
		if form.is_valid():
			form.save()
			form = get_user_profile_form(user=request.user) #return to the profile form
			messages.success(request, 'Senha alterada.')
			return render(request, get_template_path('index.html'), {'form' : form})
	else:
		form = ChangePasswordForm()
	return render(request, get_template_path('change-password.html'), {'form' : form})
	
@handle_exception
def retrieve_access(request):
	if request.method == 'POST':
		form = RetrieveAccessForm(request.POST)
		if form.is_valid():
			username_or_email = form.cleaned_data['username_or_email']
			if UserProfile.retrieve_access(username_or_email):
				messages.success(request, 
					'Enviamos um email para você com uma nova senha.' 
					' Se não lembrar o email que usou para cadastrar-se no Colabre,'
					' envie um email para suporte@colabre.org nos explicando sua dificuldade'
					' -- não esqueça de nos informar o nome do seu usuário.')
			else:
				messages.error(request, 
					'Não existe um usuário ou email com os dados que nos forneceu.' 
					' Se realmente não lembrar o email ou usuário que usou para cadastrar-se no Colabre,'
					' envie um email para suporte@colabre.org nos explicando sua dificuldade'
					' -- não esqueça de nos informar o nome do seu usuário.')
	else:
		form = RetrieveAccessForm()
	return render(request, get_template_path('retrieve-access.html'), {'form' : form})
