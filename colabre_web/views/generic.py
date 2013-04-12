from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from colabre_web.models import *
from django.db.models import Q
from django.core import serializers
from django.conf.urls import patterns, url

urlpatterns = patterns('colabre_web.views.generic',
    
    url(r'^parcial/buscar-cargo/$', 'partial_json_search_job_title', name= 'generic_partial_json_search_job_title'),
    url(r'^parcial/buscar-segmento/(.+)/$', 'partial_json_search_segment', name= 'generic_partial_json_search_segment'),
    url(r'^parcial/buscar-pais/$', 'partial_json_search_country', name= 'generic_partial_json_search_country'),
    url(r'^parcial/buscar-estado/$', 'partial_json_search_region', name= 'generic_partial_json_search_region'),
    url(r'^parcial/buscar-cidade/$', 'partial_json_search_city', name= 'generic_partial_json_search_city'),
    url(r'^parcial/buscar-empresa/(.+)/$', 'partial_json_search_company', name= 'generic_partial_json_search_company'),
)

@login_required
def partial_json_search_job_title(request):
    if request.method == 'POST':
        q = request.POST['q']
        segment = request.POST['segment']
        titles = None
        if (len(segment) > 0):
            titles = JobTitle.objects.filter(name__icontains=q, segment__name=segment)
        else:
            titles = JobTitle.objects.filter(name__icontains=q)
        
        list = serializers.serialize("json", titles.order_by('name')[:10])
        return HttpResponse(list, mimetype="application/json")

@login_required
def partial_json_search_segment(request, q):
    list = serializers.serialize("json", Segment.objects.filter(name__icontains=q).order_by("name")[:10])
    return HttpResponse(list, mimetype="application/json")

@login_required
def partial_json_search_country(request):
    if request.method == 'POST':
        q = request.POST['q']
        filter = Q(name__istartswith=q) | Q(code__istartswith=q)
        list = serializers.serialize("json", Country.objects.filter(filter).order_by("name")[:10], extras=('name',))
        return HttpResponse(list, mimetype="application/json")

@login_required
def partial_json_search_region(request):
    if request.method == 'POST':
        q = request.POST['q']
        country = request.POST['country']
        
        filter = Q(name__istartswith=q) | Q(code__istartswith=q)
        
        if len(country) > 0:
            filter = filter & Q(Q(country__name=country) | Q(country__code=country))
            
        list = serializers.serialize("json", Region.objects.filter(filter).order_by("name")[:50], extras=('name',))
        return HttpResponse(list, mimetype="application/json")

@login_required
def partial_json_search_city(request):
    if request.method == 'POST':
        q = request.POST['q']
        country = request.POST['country']
        region = request.POST['region']
        
        filter = Q(name__istartswith=q)
        
        if len(country) > 0:
            filter = filter & Q(Q(region__country__name=country) | Q(region__country__code=country))
            
        if len(region) > 0:
            filter = filter & Q(Q(region__name=region) | Q(region__code=region))
        
        list = serializers.serialize("json", City.objects.filter(filter).order_by("name")[:50], extras=('name',))
        return HttpResponse(list, mimetype="application/json")
    
@login_required
def partial_json_search_company(request, q):
    list = serializers.serialize("json", Company.objects.filter(name__icontains=q).order_by("name")[:10])
    return HttpResponse(list, mimetype="application/json")