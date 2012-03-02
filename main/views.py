from django.http import HttpResponse
from django.template import Context, loader
from main.models import *
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
#from pymongo.errors import InvalidId
from datetime import *

def index(request):
	list = Job.objects.all().order_by('-published_at')[:100]
	t = loader.get_template('main/index.html')
	c = Context({
        'list': list,
		'test' : '1, 2, 3...'
    })
	return HttpResponse(t.render(c))

def empresas(request):
	list = Company.objects.all()
	t = loader.get_template('main/companies.html')
	c = Context({
        'list': list
    })
	return HttpResponse(t.render(c))

def empresa(request, _id):
	company = Company.objects.filter(id = _id)[0];
	t = loader.get_template('main/company.html')
	c = Context({
		'obj': company,
		't' : 'ajdsh kasjhdkajshdk'
	})
	return HttpResponse(t.render(c))

def vaga(request, id):
	return HttpResponse("detalhes da vaga %s" % id)
	
def vagas(request):
	start = datetime.now()
	#list = Job.objects.raw_query({"$where" : "(this.name + ' ' + this.description).toLowerCase().indexOf('et') > -1"})
	list = Job.objects.all()[0:2000]
	end = datetime.now()
	delta = end - start
	t = loader.get_template('main/jobs.html')
	c = Context({
		'list': list,
		'perf' : "{0}.{1} ({2})".format(delta.seconds, delta.microseconds, datetime.now())
	})
	return HttpResponse(t.render(c))
	
def vagas_busca_resultado(request, _from, to, term):
	#list = Job.search(_from, to, term, 0, 100)
	list = Job.objects.all()
	t = loader.get_template('main/partial/jobs-search-result.html')
	c = Context({
        'list': list
    })
	return HttpResponse(t.render(c))
	
def vagas_busca(request):
	return render_to_response('main/jobs-search.html')
	
def detail(request, job_id):
	try:
		j = Job.objects.get(pk=job_id)
	except Job.DoesNotExist:
		raise Http404
	return render_to_response('main/detail.html', {'job': j})

def results(request, job_id):
    return HttpResponse("You're looking at the results of poll %s." % job_id)
	
def tag(request, tag):
    return HttpResponse("tag: %s" % tag)