from main.models import *
from main.JsonResponse import JsonResponse
from django.db import connection
from django.http import HttpResponse
import time

def job_titles_suggestion(request):
	if request.GET.__contains__('termo'):
		title = "%{0}%".format(request.GET['termo'])
		cursor = connection.cursor()
		cursor.execute("select title from main_job where title like %s group by title order by title asc", [title])
		set = cursor.fetchall()[:10]
		return JsonResponse(set)
	return HttpResponse()

def search_username(request):
	if request.GET.__contains__('username'):
		time.sleep(2)
		username = request.GET['username']
		result = User.objects.filter(username=username)[0:1]
		return HttpResponse(str(len(result) == 0).lower())
	return HttpResponse("false")
	
def cities_suggestion(request):
	if request.GET.__contains__('term'):
		q = "%{0}%".format(request.GET['term'])
		cursor = connection.cursor()
		cursor.execute("select name from main_city where name like %s group by name order by name asc", [q])
		set = cursor.fetchall()[:10]
		return JsonResponse(set)
	return HttpResponse()

def cities_by_state(request, state):
	if request.GET.__contains__('term'):
		city = "%{0}%".format(request.GET['term'])
		cursor = connection.cursor()
		cursor.execute("select city from main_location where state = %s and city like %s group by city order by city asc", [state, city])
		set = cursor.fetchall()[:10]
		return JsonResponse(set)
	return HttpResponse()

def states(request):
	cursor = connection.cursor()
	cursor.execute("select abbreviation from main_state order by abbreviation asc")
	set = cursor.fetchall()
	return JsonResponse(set)
