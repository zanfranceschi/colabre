# -*- coding: UTF-8 -*-
from colabre_web.models import Job
import shortuuid
from datetime import datetime
from urlparse import urljoin
from django.core.urlresolvers import reverse
from colabre.settings import HOST_ROOT_URL, EMAIL_CONTACT
from colabre_web.services import email
from colabre_web.signals import job_form_instance_saved, applyforjob_form_message_sent
from django.dispatch import receiver
from colabre_web.forms import JobForm, ApplyForJobForm
from colabre_web.statistics.models import JobApplication

@receiver(applyforjob_form_message_sent, sender=ApplyForJobForm)
def applyforjob_form_message_sent(sender, job_id, ip, mail_uuid, **kwargs):
	application = JobApplication()
	application.ip = ip
	application.job_id = job_id
	application.mail_uuid = mail_uuid
	application.save()

@receiver(job_form_instance_saved, sender=JobForm)
def job_form_instance_saved(sender, job, **kwargs):
	if (job.active):
		send_mail_to_admin_approve(job)
	

def send_mail_to_admin_approve(job):
	if (not job.admin_approved):
		
		profile = u'Anônimo'
		if (job.profile is not None):
			profile = job.profile.user.username
			
		company = ''
		if (job.company is not None):
			company = job.company.name
		
		message = u"""
perfil			{0}
segment			{1}
title			{2}
country			{3}
region			{4}
city			{5}
address			{6}
contact name	{7}
contact email	{8}
contact phone	{9}
company			{10}
description:
---
{11}
---

aprovar: {13}


ver: {12}
""".format(
		profile,
		job.job_title.segment.name,
		job.job_title.name,
		job.city.region.country.name,
		job.city.region.name,
		job.city.name,
		job.address,
		job.contact_name,
		job.contact_email,
		job.contact_phone,
		company,
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

def admin_approve(id, uuid):
	approved_job = Job.objects.get(id=id, uuid=uuid, admin_approved=False)
	approved_job.admin_approved = True
	approved_job.uuid = shortuuid.uuid()
	approved_job.admin_approval_date = datetime.now()
	approved_job.set_contact_email_verified()
	approved_job.contact_email_verified = True
	approved_job.save()
	return approved_job
	
def admin_disapprove(id):
	job = Job.objects.get(id=id)
	job.admin_disapprove()
	return job 

def mark_spam(jobId):
	job = Job.objects.get(id=jobId)
	job.mark_spam()
	return job
	
def unmark_spam(jobId):
	job = Job.objects.get(id=jobId)
	job.unmark_spam()
	return job

def try_approve_automatically(job):
	validated_email = Job.objects.filter(admin_approved=True, contact_email=job.contact_email).exists() 
	if(validated_email):
		job.admin_approved = True

	if (job.id is not None and not job.admin_approved):
		original = Job.objects.get(id=job.id)
		if (original.description != job.description):
			job.admin_approved = False
			
	return job.admin_approved
