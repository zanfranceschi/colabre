from datetime import date, timedelta

def get_week_days_range(year, week):
	d = date(year,1,1)
	if(d.weekday()>3):
		d = d+timedelta(7-d.weekday())
	else:
		d = d - timedelta(d.weekday())
	dlt = timedelta(days = (week-1)*7)
	return d + dlt, d + dlt + timedelta(days=6)