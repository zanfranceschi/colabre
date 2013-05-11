# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import *
from colabre_web.forms import ResumeForm
from colabre_web.models import Resume
from colabre_web.statistics.models import ResumeStatistics
from helpers import is_verified, is_not_verified_url
from django.conf.urls import patterns, url
from datetime import datetime
from dateutil.relativedelta import relativedelta
from chartit import *
from colabre_web.utils import get_week_days_range

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
	resume = None
	try:
		resume = Resume.objects.get(profile=request.user.get_profile())
	except Resume.DoesNotExist:
		messages.info(request, u'Seu currículo ainda não foi criado. '  
								u'Que tal preencher as informações abaixo e ' 
								u'tentar visualizar as estatísticas depois?')

		form = ResumeForm(profile=request.user.get_profile())
		return render(request, get_template_path('index.html'), {'form' : form })
	
	today = datetime.now().date()
	last_month = today - relativedelta(months=1)
	yesterday = today - relativedelta(days=1)
	last_week_date = today - relativedelta(weeks=1)
	last_week = get_week_days_range(last_week_date.year, last_week_date.isocalendar()[1])
	
	stats_count_total = ResumeStatistics.objects.filter(resume_id=resume.id).count()
	
	stats_count_last_month = ResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date__year=last_month.year, 
															access_date__month=last_month.month
															).count()
															
	stats_count_last_week = ResumeStatistics.objects.filter(
															resume_id=resume.id,
															access_date__range=[last_week[0], last_week[1]]
															).count()
	
	stats_count_yesterday = ResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date=yesterday, 
															).count()
															
	stats_count_today = ResumeStatistics.objects.filter(
															resume_id=resume.id, 
															access_date=today 
															).count()
	
	
	queryset = ResumeStatistics.objects.filter(
												resume_id=resume.id, 
												search_term__regex=r'^.+'
												)
	
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
					'text' : 'Os termos de busca que mais levaram a seu currículo'
				}
			}
	)
	
	queryset_all = ResumeStatistics.objects.filter(
												segment_id=resume.segment.id,
												search_term__regex=r'^.+'
												).exclude(resume_id=resume.id)
	
	ds_all = PivotDataPool(
		series = [{
			'options' : 
			{
				'source': queryset_all,
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
	chart_all = PivotChart(
		datasource = ds_all, 
		series_options = [{
			'options':
			{
				'type': 'column',
				'color' : 'rgba(150, 150, 150, 0.5)'
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
					'text' : 'Os termos de busca que mais levaram a currículos similares'
				}
			}
	)

	return render(request, get_template_path('stats.html'), {
															'charts' : [chart, chart_all],
															'chart_chart' : len(queryset) > 1,
	                    									'chart_chart_all' : len(queryset_all) > 1,
															'resume' : resume, 
															'stats_count_total' : stats_count_total,
															'stats_count_last_month' : stats_count_last_month,
															'stats_count_last_week' : stats_count_last_week,
															'stats_count_yesterday' : stats_count_yesterday,
															'stats_count_today' : stats_count_today,
															})


