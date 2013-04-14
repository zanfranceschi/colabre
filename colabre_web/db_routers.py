import colabre_web.statistics.models

class StatisticsRouter(object):
	def db_for_read(self, model, **hints):
		if issubclass(model, colabre_web.statistics.models.Statistics):
			return 'stats'
		return None
	
	def db_for_write(self, model, **hints):
		if issubclass(model, colabre_web.statistics.models.Statistics):
			return 'stats'
		return None
	
	def allow_syncdb(self, db, model):
		if db == 'stats' and issubclass(model, colabre_web.statistics.models.Statistics):
			return True
		elif db == 'default' and not issubclass(model, colabre_web.statistics.models.Statistics):
			return True
		else:
			return False