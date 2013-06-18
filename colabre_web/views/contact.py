from django.shortcuts import render
from django.core.urlresolvers import reverse
from colabre_web.models import Job
from colabre_web.forms import ContactForm, OpenContactForm
from django.conf.urls import patterns, url
from django.contrib import messages
from django.http import HttpResponseRedirect

urlpatterns = patterns('colabre_web.views.contact',
	url(r'^contatar/$', 'contact', name='contact'),
	url(r'^$', 'open_contact', name='open_contact'),
)

def open_contact(request):
	template = 'contact/index.html'
	form = OpenContactForm()
	if (request.method == 'POST'):
		if (not request.user.is_anonymous()):
			form = OpenContactForm(request.POST, user=request.user)
		else:
			form = OpenContactForm(request.POST)
			
		if (form.is_valid()):
			form.send_email()
			messages.success(request, u'Obrigado pelo contato. Seu email foi enviado e responderemos o mais breve possível.')
			return HttpResponseRedirect(reverse('colabre_web.views.contact.open_contact'))
		else:
			return render(request, template, {'form' : form })
	
	if (not request.user.is_anonymous()):
		form = OpenContactForm(user=request.user)

	return render(request, template, {'form' : form })


def contact(request):
	if request.method == 'POST':
		contact_form = ContactForm(request.POST)
		if contact_form.is_valid():
			contact_form.send_email()
			contact_message = 'Sua mensagem foi enviada com sucesso.'
			return render(request, '_contact-form.html', { 'contact_message' : contact_message })
		else:
			return render(request, '_contact-form.html', {'form' : contact_form })
	else:
		user_id = request.GET['user_id']
		subject = 'Colabre |'
		if request.GET['subject'] == 'r':
			subject += ' Oportunidade Profissional'
		else:
			job_id = request.GET['job_id']
			job = Job.objects.get(id=job_id)
			subject += ' ', job.job_title
			
		email_from = None
		if (not request.user.is_anonymous()):
			email_from = request.user.email

		return render(request, '_contact-form.html', {'form' : ContactForm(user_id=user_id, subject=subject, email_from=email_from)})
	
	