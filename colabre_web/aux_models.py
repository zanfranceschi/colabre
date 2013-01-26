from django.template.loader import get_template
from django.core.mail import send_mail
import colabre.settings

class BusinessException(Exception):
	""" Business Exception raised to differenciate from System Exceptions """
	pass

# convert documents to objects
class Struct:
	def __init__(self, **entries): 
		self.__dict__.update(entries)
	
class RealUserNotification:

	@staticmethod
	def notify_password_change(user, new_password):
		tbody = get_template('my-profile/email/usernotification-notify_password_change-body.txt')
		
		context = Context({
			'name' : user.first_name,
			'password' : new_password,
			'url' : colabre.settings.HOST_ROOT_URL,
		})
	
		send_mail(
				u'Colabre | Alteração de Senha',
				tbody.render(context),
				colabre.settings.EMAIL_FROM, 
				[user.email], 
				fail_silently=False)	

	@staticmethod
	def notify(user_profile, verification_uuid):
		tbody = get_template('my-profile/email/usernotification-notify-body.txt')
		ttitle = get_template('my-profile/email/usernotification-notify-title.txt')
		
		context = Context({
			'name' : user_profile.user.first_name,
			'uuid' : verification_uuid,
			'url' : colabre.settings.HOST_ROOT_URL,
		})
	
		send_mail(
				ttitle.render(Context({})),
				tbody.render(context),
				colabre.settings.EMAIL_FROM, 
				[user_profile.user.email], 
				fail_silently=False)

class DummyUserNotification:

	@staticmethod
	def notify_password_change(user, new_password):
		pass
		
	@staticmethod
	def notify(user_profile, verification_uuid):
		pass

class UserNotification:
	
	@staticmethod
	def getNotification():
		return DummyUserNotification