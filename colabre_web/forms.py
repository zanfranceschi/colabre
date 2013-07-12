# -*- coding: UTF-8 -*-
from django import forms
from models import *
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import validators
import re
from django.forms import ModelForm, extras
from datetime import datetime
import logging
import signals

logger = logging.getLogger('app')


def set_bbcode(field):
	field.widget.attrs['class'] += ' bbcode'

def custom_init(instance):
	for field in instance.fields:
		try:			
			if isinstance(instance.fields[field].widget, forms.Textarea):
				if ('class' in instance.fields[field].widget.attrs):
					instance.fields[field].widget.attrs['class'] += ' input-xxlarge'
				else:
					instance.fields[field].widget.attrs['class'] = 'input-xxlarge'
					
			if isinstance(instance.fields[field], forms.CharField) or isinstance(instance.fields[field], forms.PasswordInput):
				if ('class' in instance.fields[field].widget.attrs):
					instance.fields[field].widget.attrs['class'] += ' input-xlarge'
				else:
					instance.fields[field].widget.attrs['class'] = 'input-xlarge'
			
			if 'typeahead' in instance.fields[field].widget.attrs:
				instance.fields[field].widget.attrs['autocomplete'] = 'off'
				del instance.fields[field].widget.attrs['typeahead']
			
			if 'address' in field:
				pass
				#instance.fields[field].widget.attrs['title'] = 'Não inclua o complemento se desejar integração com o Google Maps (futuro recurso).'
	
			if 'date' in field:
				if 'class' in instance.fields[field].widget.attrs:
					instance.fields[field].widget.attrs['class'] += ' date-input'
				else:
					instance.fields[field].widget.attrs['class'] = 'date-input'
					
			if 'tags' in field:
				if 'class' in instance.fields[field].widget.attrs:
					instance.fields[field].widget.attrs['class'] += ' tags'
				else:
					instance.fields[field].widget.attrs['class'] = 'tags'
	
				if 'style' in instance.fields[field].widget.attrs:
					instance.fields[field].widget.attrs['style'] += ' width: 200px;'
				else:
					instance.fields[field].widget.attrs['style'] = 'width: 200px;'
			
			if instance.fields[field].required:
				#instance.fields[field].widget.attrs.update({'required' : ''})
				if 'class' in instance.fields[field].widget.attrs:
					instance.fields[field].widget.attrs['class'] += ' required'
				else:
					instance.fields[field].widget.attrs['class'] = 'required'
				
				if (instance.fields[field].label is not None):
					instance.fields[field].label += u'*'
		except:
				logger.exception("-- colabre_web/forms.py, custom_init --")
			
def validate_username_unique(value):
	'''Custom validator for user uniqueness.'''
	if User.objects.filter(username=value).exists():
		raise ValidationError(u'Este nome de usuário não está disponível.')
		
def validate_email_unique(value):
	pass
	'''Custom validator for email uniqueness.'''
	"""
	if User.objects.filter(email=value).exists():
		raise ValidationError(u'Este email já está cadastrado para outro usuário.')
	"""

class BaseForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(BaseForm, self).__init__(*args, **kwargs)
		custom_init(self)

class BaseModelForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BaseModelForm, self).__init__(*args, **kwargs)
		custom_init(self)

def get_user_profile_form(*args, **kwargs):
	user = kwargs['user']
	profile = UserProfile.objects.get(user=user)
	if profile.is_from_oauth:
		return UserProfileFormOAuth(*args, **kwargs)
	else:
		return UserProfileFormColabre(*args, **kwargs)

class UserProfileFormOAuth(BaseForm):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UserProfileFormOAuth, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['country_name', 'region_name', 'city_name', 'profile_type', 'birthday', 'gender']
		if self.user:
			profile = UserProfile.objects.get(user=self.user)
			
			country = None
			if profile.city and profile.city.region:
				country = profile.city.region.country
				
			region = None
			if profile.city:
				region = profile.city.region
			
			data = {
				'country_name' : country,
				'region_name' :  region,
				'city_name' : profile.city,
				'profile_type' : profile.profile_type or 'JS',
				'birthday' :  profile.birthday,
				'gender' :  profile.gender,
			}
			self.initial = data

	CHOICES_YEAR = range(datetime.now().year - 14, 1919, -1)

	country_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		required=True,
		max_length=60,
		label='País'
	)
		
	region_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		required=True,
		max_length=60,
		label='Estado'
	) 

	city_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		required=True,
		max_length=60,
		label='Cidade'
	)

	profile_type = forms.ChoiceField(
		required=True,
		label='Tipo de Perfil',
		help_text='Selecione o que melhor descreve seu objetivo no Colabre para otimizarmos o serviço para você. '
					'Por favor, note que esta opção afeta apenas a disposição do menu.',  
		choices=(('JS', 'Buscar Vagas'), ('JP', 'Publicar Vagas')),
		widget=forms.RadioSelect(),
	)
	
	birthday = forms.DateField(
		required=True,
		label='Data de Nascimento',
		widget=extras.SelectDateWidget(years=CHOICES_YEAR))
	
	gender = forms.ChoiceField(
		required=True,
		label='Sexo',
		choices=(('F', 'Feminino'), ('M', 'Masculino')),
		widget=forms.RadioSelect()
	)
	
	def save(self, commit=True):
		UserProfile.update_profile_oauth(
			self.user, 
			self.cleaned_data['profile_type'],
			self.cleaned_data['gender'],
			self.cleaned_data['birthday'],
			self.cleaned_data['country_name'],
			self.cleaned_data['region_name'],
			self.cleaned_data['city_name']
		)

class UserProfileFormColabre(UserProfileFormOAuth):
	def __init__(self, *args, **kwargs):
		super(UserProfileFormColabre, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['first_name', 'last_name', 'country_name', 'region_name', 'city_name', 'email', 'profile_type', 'birthday', 'gender', 'password']
		if self.user:
			profile = UserProfile.objects.get(user=self.user)
			data = {
				'email' : profile.user.email,
				'profile_type' : profile.profile_type or 'JS',
				'first_name' : profile.user.first_name,
				'last_name' : profile.user.last_name,
				'birthday' :  profile.birthday,
				'gender' :  profile.gender,
			}
			self.initial.update(data)
	

	first_name = forms.CharField(max_length=20, label='Primeiro Nome')
	last_name = forms.CharField(max_length=20, label='Sobrenome', help_text='Se tiver mais de um sobrenome, coloque todos aqui se desejar.')
	email = forms.EmailField(widget=forms.TextInput(),
		help_text='Se alterar seu email, será necessário verificá-lo.', 
		label='Email')
	password = forms.CharField(
		widget=forms.PasswordInput,
		help_text=u'Para atualizar seu cadastro é necessário colocar sua senha.', 
		error_messages = { 
			'required' : u'Para atualizar seu cadastro é necessário colocar sua senha.'
		},
		label='Senha'
	)
	
	def clean(self):
		super(UserProfileFormOAuth, self).clean()
		if self.is_valid():
			password = self.cleaned_data['password']
			username = self.user.username
			#email = self.cleaned_data['email']
			
			_user = authenticate(username=username, password=password)
			if _user is None:
				self._errors['password'] = u'Senha incorreta.'
			
			"""
			if self.user and User.objects.filter(Q(Q(email=email), ~Q(id=self.user.id))).exists():
				self._errors['email'] = u'O email %s já está cadastrado para outro usuário.' % email
			"""
			
			return self.cleaned_data
			
	def save(self, commit=True):
		UserProfile.update_profile(
			self.user, 
			self.cleaned_data['first_name'],
			self.cleaned_data['last_name'],
			self.cleaned_data['email'],
			self.cleaned_data['profile_type'],
			self.cleaned_data['gender'],
			self.cleaned_data['birthday'],
			self.cleaned_data['country_name'],
			self.cleaned_data['region_name'],
			self.cleaned_data['city_name']
		)


class OpenContactForm(BaseForm):
	name = forms.CharField(
		max_length=60, 
		label='Seu nome',
	)
	email_from = forms.EmailField(label='Seu email', required=True)
	subject = forms.CharField(
		max_length=60, 
		label='Assunto',
	)
	message = forms.CharField(
		label='Mensagem',
		required=True,
		help_text=u'Máximo de 700 caracteres',
		max_length=700, 
		widget=forms.Textarea(attrs={'rows' : 10, 'cols' : 40})
	)
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(OpenContactForm, self).__init__(*args, **kwargs)
		if self.user:
			self.initial.update({ 'email_from' : self.user.email })
			self.initial.update({ 'name' : self.user.get_full_name() })

	def send_email(self):
		subject = self.cleaned_data['subject']
		email_from = self.cleaned_data['email_from']
		message = self.cleaned_data['message']
		if self.user is not None:
			message = message + """
---
user		{0}
email		{1}
name		{2}
""".format(self.user.username, self.user.email, self.user.get_full_name())
		send_mail(
				subject,
				message,
				email_from, 
				[colabre.settings.EMAIL_CONTACT],
				fail_silently=False)


class ContactForm(BaseForm):
	user_id = forms.CharField(widget=forms.HiddenInput())
	subject = forms.CharField(widget=forms.HiddenInput())
	email_from = forms.EmailField(label='Seu email', required=True)
	message = forms.CharField(
		label='Mensagem',
		required=True,
		help_text=u'Máximo de 700 caracteres',
		max_length=700, 
		widget=forms.Textarea(attrs={'rows' : 5, 'cols' : 60})
	)
	
	def __init__(self, *args, **kwargs):
		user_id = kwargs.pop('user_id', None)
		subject = kwargs.pop('subject', None)
		email_from = kwargs.pop('email_from', None)
		super(ContactForm, self).__init__(*args, **kwargs)
		if user_id:
			self.user = User.objects.get(id=user_id)
			self.initial.update({ 'user_id' : user_id })
		if subject:
			self.initial.update({ 'subject' : subject })
		if email_from:
			self.initial.update({ 'email_from' : email_from })
		

	def send_email(self):
		user_id = self.cleaned_data['user_id']
		subject = self.cleaned_data['subject']
		user = User.objects.get(id=user_id)
		email_to = user.email
		email_from = self.cleaned_data['email_from']
		message = self.cleaned_data['message']
		send_mail(
				subject,
				message,
				email_from, 
				[email_to], 
				fail_silently=False)


class LoginForm(BaseForm):
	username = forms.CharField(
		max_length=30, 
		label='Usuário',
		error_messages = { 
			'required' : u'Informe seu usuário.'
		},
	)
	password = forms.CharField(
		widget=forms.PasswordInput, 
		label='Senha',
		error_messages = { 
			'required' : u'Informe sua senha.'
		},
	)
	next = forms.CharField(widget=forms.HiddenInput, required=False)


class JobForm(BaseForm):
	
	job_title_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		max_length=50, 
		required=True,
		label='Cargo',
		help_text=u'Exemplos: Analista de Sistemas, Enfermeiro, Auxiliar de Expedição, etc.'
	)
	
	segment_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		max_length=50,
		required=True, 
		label='Segmento',
		help_text=u'Segmento da vaga. Ex.: Finanças, Tecnologia da Informação, Medicina, etc.' 
	)
	
	description = forms.CharField(
		max_length=5000, 
		required=True,
		label=u'Descrição da Vaga',
		widget = forms.Textarea(attrs={'rows' : 15, 'cols' : 70}),
		help_text = u'Coloque as principais atividades que serão ser exercidas, benefícios, requisitos para os candidatos, etc.'
	)
	
	address = forms.CharField(
		max_length=120,
		required=False,
		label='Endereço',
		help_text=u'Coloque o endereço completo ou parcial, apenas bairro, região, ou outra informação relevante.',
		widget=forms.TextInput(attrs={'class' : 'large'})
	)
	
	country_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		max_length=60, 
		label=u'País',
		required=True
	)
	
	region_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		max_length=60, 
		label=u'Estado',
		required=True
	)
	
	city_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		max_length=60, 
		label='Cidade',
		required=True
	)
	
	company_name = forms.CharField(
		max_length=50, 
		label=u'Empresa',
		help_text=u'Empresa para a qual o contratado irá trabalhar ou ficar alocado.',
		required=False
	)
	
	contact_name = forms.CharField(
		max_length=60,
		required=True,
		label='Nome do Contato',
	)
	
	contact_email = forms.CharField(
		max_length=254,
		required=True,
		label='Email para Contato',
	)
	
	contact_phone = forms.CharField(
		max_length=25,
		required=False,
		label='Telefone para Contato',
	)
	
	def admin_save(self):
		job = self.job or Job()
		
		job.profile = self.profile or job.profile
		job.address = self.cleaned_data['address']
		job.description = self.cleaned_data['description']
		job.contact_name = self.cleaned_data['contact_name']
		job.contact_email = self.cleaned_data['contact_email']
		job.contact_phone = self.cleaned_data['contact_phone']
		
		job.segment_name = self.cleaned_data['segment_name']
		job.job_title_name = self.cleaned_data['job_title_name']
		job.country_name = self.cleaned_data['country_name']
		job.region_name = self.cleaned_data['region_name']
		job.city_name = self.cleaned_data['city_name']
		job.company_name = self.cleaned_data['company_name']
		job.set_contact_email_verified()
		
		job.admin_approved = True
		signals.job_form_before_instance_saved.send(sender=JobForm, job=job)
		job.save()

		return job
	
	def save(self):
		job = self.job or Job()
		
		job.profile = self.profile or job.profile
		job.address = self.cleaned_data['address']
		job.description = self.cleaned_data['description']
		job.contact_name = self.cleaned_data['contact_name']
		job.contact_email = self.cleaned_data['contact_email']
		job.contact_phone = self.cleaned_data['contact_phone']
		
		job.segment_name = self.cleaned_data['segment_name']
		job.job_title_name = self.cleaned_data['job_title_name']
		job.country_name = self.cleaned_data['country_name']
		job.region_name = self.cleaned_data['region_name']
		job.city_name = self.cleaned_data['city_name']
		job.company_name = self.cleaned_data['company_name']
		job.set_contact_email_verified()
		
		if (job.id is not None):
			original = Job.objects.get(id=job.id)
			if (original.description != job.description):
				job.admin_approved = False
		
		signals.job_form_before_instance_saved.send(sender=JobForm, job=job)
		
		job.save()

		return job
	
	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		self.job = kwargs.pop('job', None)
		super(JobForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = [
							'segment_name', 
							'job_title_name', 
							'description', 
							'country_name',
							'region_name',
							'city_name',
							'address',
							'company_name', 
							'contact_name',
							'contact_email', 
							'contact_phone']
			
		if (self.job is None): # new job
			
			if (self.profile is not None): # bring last posted job data...
				last_posted_jobs = Job.objects.filter(profile=self.profile).order_by("-id")[:1]
				last_posted_job = last_posted_jobs[0] if last_posted_jobs else None
			
				if (last_posted_job is not None):
					self.initial.update({
						#'job_title_name' 	: last_posted_job.job_title,
						'segment_name' 		: last_posted_job.job_title.segment,
						#'description' 		: last_posted_job.description,
						#'address' 			: last_posted_job.address,
						'country_name' 		: last_posted_job.city.region.country,
						#'region_name' 		: last_posted_job.city.region,
						#'city_name' 		: last_posted_job.city,
						'company_name' 		: last_posted_job.company,
						'contact_name' 		: last_posted_job.contact_name,
						'contact_email'		: last_posted_job.contact_email,
						'contact_phone' 	: last_posted_job.contact_phone
					})
		else: # existing job
			self.initial = {
				'job_title_name' 	: self.job.job_title,
				'segment_name' 		: self.job.job_title.segment,
				'description' 		: self.job.description,
				'address' 			: self.job.address,
				'country_name' 		: self.job.city.region.country,
				'region_name' 		: self.job.city.region,
				'city_name' 		: self.job.city,
				'company_name' 		: self.job.company,
				'contact_name' 		: self.job.contact_name,
				'contact_email' 	: self.job.contact_email,
				'contact_phone' 	: self.job.contact_phone,
			}


	
class ValidateJobForm(BaseForm):
	uuid = forms.CharField(
		max_length=60,
		label='Código',
		help_text='Entre com o código informado.', 
		required=True
	)

class ResumeForm(BaseForm):

	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		super(ResumeForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = [
							'visible',
							'segment_name',
							'short_description',
							'full_description',
							]
		set_bbcode(self.fields['full_description'])
		if self.profile:
			self.resume = None
			try:
				self.resume = Resume.objects.get(profile=self.profile)
			except Resume.DoesNotExist:
				self.initial = { 'visible' : True }
			if self.resume:
				data = {
					'segment_name' : self.resume.segment_name,
					'short_description' : self.resume.short_description,
					'full_description' : self.resume.full_description,
					'visible' : self.resume.visible
				}
				self.initial = data
	
	segment_name = forms.CharField(
		widget=forms.TextInput(attrs={'typeahead' : 'true'}),
		label='Segmento',
		help_text='Coloque o segmento do seu campo de trabalho. Por exemplo: Tecnologia da Informação',
		max_length=50
	)
	
	short_description = forms.CharField(
		label='Mini currículo',
		help_text='Seu mini currículo. Coloque uma breve descrição contendo suas principais habilidades e/ou formação em até 250 caracteres.',
		max_length=250, 
		widget=forms.Textarea(attrs={'rows' : 3, 'cols' : 80})
	)
	full_description = forms.CharField(
		label='Currículo Completo',
		help_text='Se estiver copiando e colando do Word, verifique seu currículo na página de currículos após ter salvo; ele pode ficar desformatado.',
		max_length=5000, widget=forms.Textarea(attrs={'rows' : 15, 'cols' : 80})
	)
	
	visible = forms.BooleanField(
		label=u'Visível',
		help_text=u'Quando este campo estiver desmarcado, seu currículo não será mostrado nas buscas.',
		required=False
	)
	
	def save(self, commit=True):
		Resume.save_(
			self.profile,
			self.cleaned_data['segment_name'],
			self.cleaned_data['short_description'], 
			self.cleaned_data['full_description'], 
			self.cleaned_data['visible'])

class RetrieveAccessForm(BaseForm):
	username_or_email = forms.CharField(
		label='Usuário ou Email', 
		help_text='Por favor, coloque seu usuário ou email para tentarmos recuperar seu acesso ao Colabre.'
	)

class ChangePasswordForm(BaseForm):
	user = None
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	current_password = forms.CharField(
		widget=forms.PasswordInput, 
		label='Senha Atual')
	new_password = forms.CharField(
		widget=forms.PasswordInput, 
		help_text='Nova senha.', 
		label='Nova Senha')
	confirm_new_password = forms.CharField(
		widget=forms.PasswordInput, 
		help_text='Confirme sua nova senha.', 
		label='Confirme sua Nova Senha')
	
	def clean(self):
		super(forms.Form, self).clean()
		if self.is_valid():
			password = self.cleaned_data['current_password']
			username = self.user.username
			
			_user = authenticate(username=username, password=password)
			
			if _user is None:
				self._errors['current_password'] = u'Senha incorreta.'
			elif 'new_password' in self.cleaned_data and 'confirm_new_password' in self.cleaned_data:
				if self.cleaned_data['new_password'] != self.cleaned_data['confirm_new_password']:
					self._errors['new_password'] = u'As senhas devem ser iguais.'
					self._errors['confirm_new_password'] = u'As senhas devem ser iguais.'
		return self.cleaned_data
		
	def save(self, commit=True):
		self.user.set_password(self.cleaned_data['new_password'])
		self.user.save()

class RegisterForm(BaseForm):

	username = forms.CharField(
				max_length=30,
				help_text=u'Usuário com no máximo 30 caracteres. Você pode usar letras, dígitos e os símbolos @ . + - _.', 
				label='Usuário', 
				validators=[
					validate_username_unique,
					validators.RegexValidator(regex=re.compile(r'^[\d\w@\+\-_\.]{,30}$'), code='invalid')
					],
				error_messages = { 'invalid' : u'Usuário com no máximo 30 caracteres. Você pode usar letras, dígitos e @/./+/-/_.' }
					
				)
								
	email = forms.EmailField(
				help_text='Seu email.', 
				label='Email', 
				validators=[validate_email_unique]
				)

	password = forms.CharField(
				widget=forms.PasswordInput, 
				help_text='Senha.', 
				label='Senha'
				)
								
	confirm_password = forms.CharField(
					widget=forms.PasswordInput, 
					help_text='Confirme a senha digitada anteriormente.', 
					label='Confirme a Senha'
					)
	
	def clean(self):
		'''Required custom validation for the form.'''
		super(forms.Form, self).clean()
		if 'password' in self.cleaned_data and 'confirm_password' in self.cleaned_data:
			if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
				self._errors['password'] = u'As senhas devem ser iguais.'
				self._errors['confirm_password'] = u'As senhas devem ser iguais.'
		return self.cleaned_data
		
	def save(self):
		return UserProfile.create(
			self.cleaned_data['username'],
			self.cleaned_data['email'],
			self.cleaned_data['password']
		)
