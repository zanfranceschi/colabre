from pymongo import MongoClient
from datetime import *

class AccessTracker:
	
	@classmethod
	def handle_access(cls, request):
		'''
		HTTP_REFERER: http://127.0.0.1:8000/
		PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 42 Stepping 7, GenuineIntel
		REQUEST_METHOD: GET
		QUERY_STRING:
		HTTP_USER_AGENT: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)
		HTTP_COOKIE: csrftoken=Htyt4gjAbZqr8QymuN0gu1S3sjKDKBsf; sessionid=116e386558a8c80b8291e62aa2954c09
		REMOTE_ADDR: 127.0.0.1
		PROCESSOR_ARCHITECTURE: AMD64
		CSRF_COOKIE: Htyt4gjAbZqr8QymuN0gu1S3sjKDKBsf
		HTTP_HOST: 127.0.0.1:8000
		PATH_INFO: /
		HTTP_ACCEPT_LANGUAGE: pt-BR
		NUMBER_OF_PROCESSORS: 4
		OS: Windows_NT
		'''
		access = {
			'HTTP_REFERER' 				: request.META['HTTP_REFERER'],
			'PROCESSOR_IDENTIFIER' 		: request.META['PROCESSOR_IDENTIFIER'],
			'REQUEST_METHOD' 			: request.META['REQUEST_METHOD'],
			'QUERY_STRING' 				: request.META['QUERY_STRING'],
			'HTTP_USER_AGENT' 			: request.META['HTTP_USER_AGENT'],
			'HTTP_COOKIE' 				: request.META['HTTP_COOKIE'],
			'REMOTE_ADDR' 				: request.META['REMOTE_ADDR'],
			'PROCESSOR_ARCHITECTURE' 	: request.META['PROCESSOR_ARCHITECTURE'],
			'CSRF_COOKIE' 				: request.META['CSRF_COOKIE'],
			'PATH_INFO' 				: request.META['PATH_INFO'],
			'HTTP_ACCEPT_LANGUAGE' 		: request.META['HTTP_ACCEPT_LANGUAGE'],
			'NUMBER_OF_PROCESSORS' 		: request.META['NUMBER_OF_PROCESSORS'],
			'OS' 						: request.META['NUMBER_OF_PROCESSORS'],
			'ACCESS_DATETIME' 			: datetime.now(),
			}
			
		connection = MongoClient()
		db = connection.colabre
		db.accesses.insert(access)
