from django.core.mail import send_mail
from colabre.settings import EMAIL_FROM

def send(title, message, recipient_list):
	send_mail(
		u"Colabre | {0}".format(title),
        message,
        EMAIL_FROM, 
        recipient_list, 
        fail_silently=False)