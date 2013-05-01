# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import *
from colabre_web.forms import ResumeForm
from colabre_web.models import Resume
from colabre_web.statistics.models import MyResumeStatistics
from helpers import is_verified, is_not_verified_url
from django.conf.urls import patterns, url
from datetime import datetime
from dateutil.relativedelta import relativedelta
from chartit import *

urlpatterns = patterns('colabre_web.views.my_resume',
	url(r'^$', 'index', name='my_resume_index'),
	url(r'^estatisticas/$', 'stats', name='my_resume_stats'),
)

def get_template_path(template):
	return 'my-resume/%s' % template

@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def index(request):
	if request.method == 'POST':
		
		"""test"""
		"""
		import sys
		segments = request.POST.getlist('segment')
		
		for segment in segments:
			print >> sys.stderr, segment
		"""

		form = ResumeForm(request.POST, profile=request.user.get_profile())
		if form.is_valid():
			form.save()
			messages.success(request, u'Currículo atualizado.')
	else:
		form = ResumeForm(profile=request.user.get_profile())
	return render(request, get_template_path('index.html'), {'form' : form })


@login_required
@user_passes_test(is_verified, login_url=is_not_verified_url)
def stats(request):
	resume = Resume.objects.get(profile=request.user.get_profile())
	
	today = datetime.now().date()
	last_month = today - relativedelta(months=1)
	yesterday = today - relativedelta(days=1)
	
	stats_count_total = MyResumeStatistics.objects.filter(resume_id=resume.id).count()
	
	stats_count_last_month = MyResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date__year=last_month.year, 
															access_date__month=last_month.month
															).count()
															
	stats_count_yesterday = MyResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date=yesterday, 
															).count()
															
	stats_count_today = MyResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date=today 
															).count()
	
	
	queryset = MyResumeStatistics.objects.filter(
												resume_id=resume.id, 
												search_term__regex=r'^.+'
												)
	#queryset.query.having = ['COUNT(resume_id) > 1']
	
	ds = PivotDataPool(
		series = [{
			'options' : 
			{
				'source': queryset,
				'categories' : 'search_term'
			},
			'terms' : 
			{
				'Quantidade': Count('search_term'),
			}
		}],
		top_n_term = 'Quantidade',
		top_n = 6
	)
	chart = PivotChart(
		datasource = ds, 
		series_options = [{
			'options':
			{
				'type': 'column',
				'color' : 'rgba(70, 114, 193, 1)'
			},
			'terms': 
			[	
				'Quantidade', 
			],
		}], chart_options = {
				'chart' : 
				{
					'backgroundColor' : 'rgba(255, 255, 255, 0.0)'		
				},
				'yAxis' : 
				{
					'title' :
					{
						'text' : ' '
					}
				},
				'legend' :
				{
					'enabled' : False
				},
				'xAxis' : 
				{
					'title' :
					{
						'text' : ' '
					}
				},
				'title' : 
				{
					'text' : 'Os 6 termos de busca que mais levaram a seu currículo'
				}
			}
	)

	return render(request, get_template_path('stats.html'), {
															'chart' : chart,
															'resume' : resume, 
															'stats_count_total' : stats_count_total,
															'stats_count_last_month' : stats_count_last_month,
															'stats_count_yesterday' : stats_count_yesterday,
															'stats_count_today' : stats_count_today,
															})


