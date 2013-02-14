#from django.core import serializers
from tasks import *


def log_request(request):
	request_META = request.META.copy()
	celery_log_request.delay(request_META)

def log_job_request(request, search_term, job):
	import sys
	print >> sys.stderr,  request.META.__class__.__name__
	#celery_log_job_request.delay(request, search_term, job)
	
def log_resume_request(request, search_term, resume):
	pass
	#celery_log_resume_request.delay(request, search_term, resume)