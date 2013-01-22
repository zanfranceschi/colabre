# -*- coding: UTF-8 -*-
from django import forms
from models import *
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import validators
import re
from django.forms import ModelForm
from datetime import datetime
import time

def set_bbcode(field):
	field.widget.attrs['class'] += ' bbcode'

def custom_init(instance):
	for field in instance.fields:
		
		if 'address' in field:
			instance.fields[field].widget.attrs['title'] = 'Não inclua o complemento se desejar integração com o Google Maps (futuro recurso).'

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
			if 'class' in instance.fields[field].widget.attrs:
				instance.fields[field].widget.attrs['class'] += ' required'
			else:
				instance.fields[field].widget.attrs['class'] = 'required'
			instance.fields[field].label += '*'
			
def validate_username_unique(value):
	'''Custom validator for user uniqueness.'''
	if User.objects.filter(username=value).exists():
		raise ValidationError(u'Este nome de usuário não está disponível.')
		
def validate_email_unique(value):
	pass
	'''Custom validator for email uniqueness.'''
	if User.objects.filter(email=value).exists():
		raise ValidationError(u'Este email já está cadastrado para outro usuário.')

class BaseForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(BaseForm, self).__init__(*args, **kwargs)
		custom_init(self)

class BaseModelForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BaseModelForm, self).__init__(*args, **kwargs)
		custom_init(self)

class UserProfileForm(BaseForm):
	user = None
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UserProfileForm, self).__init__(*args, **kwargs)
		if self.user:
			profile = UserProfile.objects.get(user=self.user)

			data = {
				'email' : profile.user.email,
				'profile_type' : profile.profile_type,
				'first_name' : profile.user.first_name,
				'last_name' : profile.user.last_name,
				'birthday' :  profile.birthday,
				'gender' :  profile.gender,
			
			}
			if profile.resume:
				data.update({
					'resume_short_description' : profile.resume.short_description,
					'resume_full_description' : profile.resume.full_description	
				})
			self.initial = data
	

	first_name = forms.CharField(max_length=20, label='Primeiro Nome')
	last_name = forms.CharField(max_length=20, label='Sobrenome', help_text='Se tiver mais de um sobrenome, coloque todos aqui se desejar.')
	email = forms.EmailField(widget=forms.TextInput(),
				help_text='Se alterar seu email, será necessário verificá-lo.', 
				label='Email')

	profile_type = forms.ChoiceField(
		required=False,
		label='Tipo de Perfil',
		help_text='Selecione o que melhor descreve seu objetivo no Colabre para otimizarmos o conteúdo para você.', 
		choices=(('', '--- Selecione ---'),('js', 'Buscar Vagas'), ('jp', 'Publicar Vagas')),
		widget=forms.Select()
	
	)
	gender = forms.ChoiceField(
		required=True,
		label='Sexo',
		choices=(('U', 'Indefinido'),('M', 'Masculino'), ('F', 'Feminino')),
		widget=forms.Select()
	)
	birthday = forms.DateField(
		required=True,
		label='Data do seu nascimento',
		help_text='Entre com a data do seu nascimento. Note que esse serviço só pode ser usado por maiores de 16 anos.'
	)
	password = forms.CharField(
				widget=forms.PasswordInput,
				help_text=u'Para atualizar seu cadastro, é necessário colocar sua senha.', 
				error_messages = { 
					'required' : u'Para atualizar seu cadastro, é necessário colocar sua senha.'
				},
				label='Senha'
	)
	
	def clean(self):
		super(forms.Form, self).clean()
		if self.is_valid():
			from dateutil.relativedelta import relativedelta
			current_date = date.today()
			user_birthday = self.cleaned_data['birthday']
			
			diff = relativedelta(current_date, user_birthday)
			
			print >> sys.stderr, diff
			#print >> sys.stderr, 
			
			if diff.years < 16:
				self._errors['birthday'] = u'Você tem menos de 16 anos. Com isso, você não poderá usar os serviços do Colabre.'
		
			password = self.cleaned_data['password']
			username = self.user.username
			email = self.cleaned_data['email']
			
			_user = authenticate(username=username, password=password)
			
			if _user is None:
				self._errors['password'] = u'Senha incorreta.'
			
			if self.user and User.objects.filter(Q(Q(email=email), ~Q(id=self.user.id))).exists():
				self._errors['email'] = u'O email %s já está cadastrado para outro usuário.' % email
			
			return self.cleaned_data
			
	def save(self, commit=True):
		UserProfile.update_profile(
			self.user, 
			self.cleaned_data['first_name'],
			self.cleaned_data['last_name'],
			self.cleaned_data['email'],
			self.cleaned_data['profile_type'],
			self.cleaned_data['gender'],
			self.cleaned_data['birthday']
		)
	
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

class JobForm(ModelForm):
	profile = None
	
	'''
		profile								title
		workplace_political_location		workplace_political_location_name
		workplace_location					description
		segment								segment_name
		company								company_name
		contact_email						contact_phone
		creation_date						published
	'''

	class Meta:
		model = Job
		exclude = ('job_title', 'profile', 'segment', 'company', 'workplace_political_location', 'date_creation')
		fields = (
			'job_title_name', 
			'segment_name',
			'description',
			'workplace_political_location_name',
			'workplace_location', 
			#'published',
			'company_name', 
			'contact_email', 
			'contact_phone')
	
	def save(self, commit=True):
		self.instance.profile = self.profile
		self.instance.save()
	
	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		super(JobForm, self).__init__(*args, **kwargs)
		self.fields['job_title_name'].label = u'Título'
		self.fields['job_title_name'].help_text = u'Exemplos: Analista de Sistemas, Enfermeiro, Auxiliar de Expedição, etc.'
		self.fields['segment_name'].label = u'Segmento da Vaga'
		self.fields['segment_name'].help_text = u'Segmento da vaga. Ex.: Finanças, Tecnologia da Informação, Medicina, etc..'
		self.fields['workplace_political_location_name'].label = u'Cidade'
		self.fields['workplace_political_location_name'].help_text = u'Cidade da vaga.'
		self.fields['description'].label = u'Descrição da Vaga'
		self.fields['description'].help_text = u'Coloque as principais atividades que serão ser exercidas, benefícios, requisitos para os candidatos, etc.'
		self.fields['description'].widget = forms.Textarea(attrs={'rows' : 15, 'cols' : 70})
		self.fields['company_name'].label = u'Empresa'
		self.fields['company_name'].help_text = u'Empresa para a qual o contratado irá trabalhar ou ficar alocado.'
		self.fields['company_name'].required = False
		self.fields['contact_email'].label = u'Email para Contato'
		self.fields['contact_email'].required = False
		self.fields['contact_phone'].label = u'Telefone para Contato'
		self.fields['contact_phone'].required = False
		self.fields['workplace_location'].label = u'Endereço'
		self.fields['workplace_location'].help_text = u'Coloque o endereço completo ou parcial, apenas bairro, região, ou outra informação relevante.'
		self.fields['workplace_location'].required = False
		self.fields['workplace_location'].widget = forms.TextInput(attrs={'class' : 'large'})
		#self.fields['published'].label = u'Visível publicamente'
		#self.fields['published'].help_text = u'Se este controle estiver desmarcado, esta vaga não ficará visível publicamente -- útil para quando desejar pré-cadastrar vagas.'
		if not self.instance.id:
			self.initial = {
				'contact_email' : self.profile.user.email or None
			}
			last_posted_jobs = Job.objects.all().order_by("-id")[:1]
			if len(last_posted_jobs) > 0:
				last_posted_job = last_posted_jobs[0]
				self.initial.update({
					'company_name' : last_posted_job.company_name,
					'segment_name' : last_posted_job.segment_name,
					'workplace_political_location_name' : last_posted_job.workplace_political_location_name,
					'workplace_location' : last_posted_job.workplace_location,
					'contact_phone' : last_posted_job.contact_phone
				})
		custom_init(self)
	

class ResumeForm(BaseForm):

	profile = None

	def __init__(self, *args, **kwargs):
		self.profile = kwargs.pop('profile', None)
		super(ResumeForm, self).__init__(*args, **kwargs)
		#self.fields['full_description'].widget.attrs['class'] += ' bbcode'
		set_bbcode(self.fields['full_description'])
		if self.profile:
			resume = None
			try:
				resume = Resume.objects.get(profile=self.profile)
			except Resume.DoesNotExist:
				self.initial = { 'visible' : True }
			if resume:
				data = {
					'short_description' : resume.short_description,
					'full_description' : resume.full_description,
					'visible' : resume.visible
				}
				self.initial = data
	
	short_description = forms.CharField(
		label='Mini currículo',
		help_text='Seu mini currículo. Coloque uma breve descrição contendo suas principais habilidades e/ou formação em até 250 caracteres.',
		max_length=250, 
		widget=forms.Textarea(attrs={'rows' : 3, 'cols' : 80})
	)
	full_description = forms.CharField(
		label='Currículo Completo',
		# help_text='Currículo completo.',
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
			self.cleaned_data['short_description'], 
			self.cleaned_data['full_description'], 
			self.cleaned_data['visible'])
		#self.instance.profile = self.profile
		#super(ResumeForm, self).save(commit=commit)

class RetrieveAccessForm(BaseForm):
	username_or_email = forms.CharField(
		label='Usuário ou Email', 
		help_text='Por favor, coloque seu usuário ou email tentarmos para recuperar seu acesso ao Colabre.')

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
				help_text=u'Usuário com no máximo 30 caracteres. Você pode usar letras, dígitos e @/./+/-/_.', 
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
