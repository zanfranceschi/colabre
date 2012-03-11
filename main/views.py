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

def logout_view(request):
	logout(request)
	return render(request, 'login.html', { 'message' : 'Usuário deslogado.' })

def index(request):
	list = Job.objects.all().order_by('-published_at')[:100]
	data = {
        'list': list,
		'test' : '1, 2, 3...'
    }
	return render(request, 'index.html', data)

def empresas(request):
	list = Company.objects.all()
	data = {
        'list': list
    }
	return render(request, "companies.html", data)

def empresa(request, _id):
	company = Company.objects.filter(id = _id)[0];
	data = {
		'obj': company,
		't' : 'ajdsh kasjhdkajshdk'
	}
	return render(request, "company.html", data)

def vaga(request, id):
	return HttpResponse("detalhes da vaga %s" % id)
	
def vagas(request):
	start = datetime.now()
	list = Job.objects.all()[0:50]
	end = datetime.now()
	delta = end - start
	data = {
		'list': list,
		'perf' : "{0}.{1} ({2})".format(delta.seconds, delta.microseconds, datetime.now())
	}
	return render(request, "jobs.html", data)

#@login_required	
def vagas_busca_resultado(request):
	if not request.POST:
		return HttpResponse("")
	else:
		term = smart_str(request.POST['term'])
		location = smart_str(request.POST['location'])
		#date_from = datetime.strptime(request.POST['date_from'], '%Y/%m/%d')
		list = Job.objects.filter(
								  Q(title__icontains = term) | Q(description__icontains = term),
								  Q(city__icontains = location) | Q(state__icontains = location)
								).order_by("-published_at")[:1000]
		'''print "\n\n\n\n\n"
		print(str(Job.objects.filter(
								  Q(title__icontains = term)
								| Q(description__icontains = term),
								#| Q(company__name__istartswith = term),
								  #Q(published_at >= date_from),
								  Q(city__icontains = location) | Q(state__icontains = location)
								).query))
		'''
		data = {
			'list': list
		}
		return render(request, 'partial/jobs-search-result.html', data)

def vagas_busca(request):
	if request.GET:
		data = { 'data' : 'OK' }
	else:
		data = { 'data' : 'N.A.' }

	return render(request, 'jobs-search.html', data)

def detail(request, job_id):
	try:
		j = Job.objects.get(pk=job_id)
	except Job.DoesNotExist:
		raise Http404
	return render(request, 'detail.html', {'job': j})

def results(request, job_id):
    return HttpResponse("You're looking at the results of poll %s." % job_id)
	
def tag(request, tag):
    return HttpResponse("tag: %s" % tag)