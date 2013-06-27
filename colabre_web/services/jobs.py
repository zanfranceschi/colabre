# -*- coding: UTF-8 -*-
from colabre_web.models import Job
import shortuuid
from datetime import datetime
from urlparse import urljoin
from django.core.urlresolvers import reverse
from colabre.settings import HOST_ROOT_URL, EMAIL_CONTACT
from colabre_web.services import email
from django.db.models.signals import post_save
from colabre_web.signals import job_form_before_instance_saved
from django.dispatch import receiver
from colabre_web.forms import JobForm

@receiver(post_save, sender=Job, dispatch_uid='dispatcher_send_email_post_save')
def job_post_save(sender, **kwargs):
	job = kwargs['instance']
	send_mail_to_admin_approve(job)
	send_mail_to_verify_email(job)

@receiver(job_form_before_instance_saved, sender=JobForm)
def test(sender, **kwargs):
	pass
	

def send_mail_to_admin_approve(job):
	if (not job.admin_approved):
		message = u"""
public				{0}
segment				{1}
title				{2}
country				{3}
region				{4}
city				{5}
address				{6}
contact name		{7}
contact email		{8}
contact phone		{9}
description:
---
{10}
---

ver: {11}
aprovar: {12}
""".format(
		job.contact_email_verified,
		job.job_title.segment.name,
		job.job_title.name,
		job.city.region.country.name,
		job.city.region.name,
		job.city.name,
		job.address,
		job.contact_name,
		job.contact_email,
		job.contact_phone,
		job.description,
		urljoin(
			HOST_ROOT_URL,
			reverse('colabre_web.views.jobs.detail', args=(job.id,))
		),
		urljoin(
			HOST_ROOT_URL,
			reverse('colabre_web.views.admin.job_approve', args=(job.id,job.uuid,))
		)
	)
		email.send(u"Aprovação de Nova Vaga", message, [EMAIL_CONTACT])

def send_mail_to_verify_email(job):
	if (job.contact_email_verified or not job.admin_approved): 
		"Never send an email validation request for a non admin approved job"
		return

	how_to_exclude_instructions = None

	if (job.profile is None):
		how_to_exclude_instructions = u"""

Se desejar excluir a vaga, informe o código {0} no formulário do endereço {1}.
""".format(job.uuid, urljoin(
				HOST_ROOT_URL, 
				reverse('colabre_web.views.jobs.delete', args=(job.id,job.contact_email,))
			))
	

	message = u"""{0},
	
O email da vaga {1} precisa ser verificado.
Acesse {2} e informe o código {3} para validá-lo.{4}

Obrigado,

Equipe Colabre
www.colabre.org""".format(
			job.contact_name,
			job.job_title,
			urljoin(
				HOST_ROOT_URL, 
				reverse('colabre_web.views.jobs.validate_email', args=(job.id,job.contact_email,))
			),
			job.uuid,
			how_to_exclude_instructions
		)

	email.send(u"Validação de Email", message, [job.contact_email])

def admin_approve(id, uuid):
	approved_job = Job.objects.get(id=id, uuid=uuid, admin_approved=False)
	approved_job.admin_approved = True
	approved_job.uuid = shortuuid.uuid()
	approved_job.admin_approval_date = datetime.now()
	approved_job.set_contact_email_verified()
	approved_job.save()
	send_mail_to_verify_email(approved_job)
	

def validate_email(job_id, email, uuid):
	job = Job.objects.get(id=job_id, contact_email=email, uuid=uuid, contact_email_verified=False)
	job.contact_email_verified = True
	job.save()
	if (job.profile is not None):
		"""
			Validate other emails from the same profile...
		"""
		Job.objects.filter(contact_email=email, profile=job.profile, contact_email_verified=False).update(contact_email_verified=True)
	