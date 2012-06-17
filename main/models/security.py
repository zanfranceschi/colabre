import time
from datetime import *
from django.db import models
import uuid
from domain import *


class ColabreUserVerification(models.Model):
	class Meta:
		app_label = 'main'
	
	def get_uuid():
		return str(uuid.uuid4())
	
	user = models.ForeignKey(ColabreUser, unique=True)
	uuid = models.CharField(max_length=36, default=get_uuid, unique=True)
	date_verified = models.DateTimeField(null=True)
	
	def setVerified(self, uuid):
		if uuid == self.uuid:
			if self.user.is_verified:
				raise BusinessException("Usuário já verificado.")
			self.date_verified = datetime.now()
			self.user.is_verified = True
			self.save()
			self.user.save()
			return True
		else:
			return False
