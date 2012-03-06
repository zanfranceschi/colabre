from main.models import *
from main.JsonResponse import JsonResponse
from django.db import connection
from django.http import HttpResponse

def job_titles_suggestion(request):
	if request.GET.__contains__('termo'):
		title = "%{0}%".format(request.GET['termo'])
		cursor = connection.cursor()
		cursor.execute("select title from main_job where title like %s group by title order by title asc", [title])
		set = cursor.fetchall()
		return JsonResponse(set)
	return HttpResponse()