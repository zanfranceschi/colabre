from datetime import date, timedelta
import unicodedata

def strip_specialchars(s):
	return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
	#return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def get_week_days_range(year, week):
	d = date(year,1,1)
	if(d.weekday()>3):
		d = d+timedelta(7-d.weekday())
	else:
		d = d - timedelta(d.weekday())
	dlt = timedelta(days = (week-1)*7)
	return d + dlt, d + dlt + timedelta(days=6)


def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def baseurl(request):
	"""
	Return a BASE_URL template context for the current request.
	"""
	if request.is_secure():
		scheme = 'https://'
	else:
		scheme = 'http://'
	
	return {'BASE_URL' : scheme + request.get_host(),}