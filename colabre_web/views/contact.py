from django.shortcuts import render
from colabre_web.models import Job
from colabre_web.forms import ContactForm
from helpers import handle_exception
from django.conf.urls import patterns, url

urlpatterns = patterns('colabre_web.views.contact',
	url(r'^contatar/$', 'contact', name='contact'),
)

@handle_exception
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
		return render(request, '_contact-form.html', {'form' : ContactForm(user_id=user_id, subject=subject)})
	
	