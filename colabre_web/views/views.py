from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import *
from colabre_web.models import *
from colabre_web.statistics.models import *
import time
from colabre_web.forms import *
from helpers import *
from chartit import DataPool, Chart


@handle_exception
def handle_uploaded_file(f):
	with open('some/file/name.txt', 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

@handle_exception
def legal(request):
	return render(request, 'legal.html')


def chart_test(request, job_id=2001):
	data = DataPool(
           series=
            [{'options': {
               'source': JobPublicNumViews.objects.filter(job_id=job_id)},
              'terms': [
				'job_title_name',
                	{
						'Total' : 'num_views_total',
		                '06 às 10' : 'num_views_0600_0959',
		                '10 às 14' : 'num_views_1000_1359',
		                '14 às 18' : 'num_views_1400_1759',
		                '18 às 22' : 'num_views_1800_2159',
		                '22 às 06' : 'num_views_2200_0559',
					}
				]}
			])

	cht = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': False},
                'terms': {
                  'job_title_name' : 
					[
	                    'Total',
	                    '06 às 10',
	                    '10 às 14',
	                    '14 às 18',
	                    '18 às 22',
	                    '22 às 06'
                    ]
                  }}],
            chart_options = {
					'title': { 'text': 'Visualizações por faixa horária'},
					'xAxis': { 
							'title': { 'text': ' ' }, 
					},
					'yAxis': { 
							'title' : { 'text' : 'Quantidade de Visualizações'},
							'minTickInterval' : 1,

					},
				}
			)
	
	return render(request, 'chart_test.html', {'charttest' : cht})
