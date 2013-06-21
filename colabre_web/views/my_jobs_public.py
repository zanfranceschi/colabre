from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from datetime import *
from django.db import connections
from colabre_web.models import *
from colabre_web.aux_models import *
from colabre_web.forms import *
from colabre_web.statistics.models import *
from django.conf.urls import patterns, url
import logging

urlpatterns = patterns('colabre_web.views.my_jobs_public',
    
    url(r'^criar/$', 'create', name='jobs_create'),
    url(r'^editar/$', 'edit', name='jobs_edit'),
    url(r'^atualizar/$', 'update', name='jobs_update'),
    
    #url(r'^confirmar-exclusao/([\d]+)/$', 'confirm_del', name='jobs_confirm_del'),
    url(r'^excluir/([\d]+)/$', 'delete', name='jobs_delete'),
)

def get_template_path(template):
    return 'my_jobs_public/%s' % template

def create(request):
    if (not request.user.is_anonymous()):
        return HttpResponseRedirect(reverse('colabre_web.views.my_jobs.create'))
    
    if request.method == 'POST':
        """
            2º Passo para criação de vaga
                Registra a vaga e envia pedido de aprovação para o admin
        """
        form = JobForm(request.POST, public=True)
        if form.is_valid():
            created_job = form.save()
            send_mail(
                    u"Colabre | Aprovação de Nova Vaga Pública",
                    created_job.to_string(),
                    colabre.settings.EMAIL_FROM, 
                    [colabre.settings.EMAIL_CONTACT], 
                    fail_silently=False)
            messages.success(request, 
                            u'Sua vaga foi submetida para aprovação. '
                            u'A aprovação não deve levar mais do que alguns minutos e, '
                            u'assim que concluída, você receberá uma notificação por email.')
        else:
            messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
    else:
        """
            1º Passo para criação de uma vaga pública
                Formulário de criação da vaga
        """
        form = JobForm(public=True)

    return render(request, get_template_path('create.html'), {'form' : form, 'action' : '/vagas/criar/'})


def edit(request):
    if request.method == 'POST':
        public_uuid = request.POST['public_uuid']
        try:
            job = Job.objects.get(public_uuid=public_uuid)
            form = JobForm(public_uuid=public_uuid)
            return render(request, get_template_path('edit.html'), {'form' : form, 'job' : job, 'action' : '/vagas/atualizar/'})
        except Job.DoesNotExist:
            return HttpResponseRedirect(reverse('colabre_web.views.home.index'))
    else:
        form = CodeJobForm()
        return render(request, get_template_path('edit-code.html'), {'form' : form, 'action' : '/vagas/editar/'})

def update(request):
    if (request.method == 'POST'):
        form = JobForm(request.POST, public_uuid=request.POST['public_uuid'])
        if form.is_valid():
            edited_job = form.save()
            messages.success(request, 
                            u'Sua edição foi submetida para aprovação. '
                            u'A aprovação não deve levar mais do que alguns minutos e, '
                            u'assim que concluída, você receberá uma notificação por email.')
            return render(request, get_template_path('edit-code.html'), {'form' : CodeJobForm(), 'action' : '/vagas/editar/'})
            
    else:
        return HttpResponseRedirect(reverse('colabre_web.views.home.index'))
    

def delete(request, id):
    pass

"""            
def update(request):
    if request.method == 'POST':
        uuid = request.POST['uuid']
        try:
            job = Job.objects.get(public_uuid=uuid)
            form = JobForm(request.POST, uuid=uuid)
            if form.is_valid():
                edited_job = form.save()
                send_mail(
                    u"Colabre | Aprovação de Vaga Editada",
                    edited_job.to_string(),
                    colabre.settings.EMAIL_FROM, 
                    [colabre.settings.EMAIL_CONTACT], 
                    fail_silently=False)
                
                template = get_template_path('index.html')
                
                messages.success(request, 
                            u'Sua vaga foi submetida para aprovação. '
                            u'A aprovação não deve levar mais do que alguns minutos e, '
                            u'assim que concluída, você receberá uma notificação por email.')
            else:
                template = get_template_path('edit.html')
                messages.error(request, 'Por favor, verifique o preenchimento da vaga.')
        except Job.DoesNotExist:
            pass
    else:
        template = get_template_path('edit.html')
        form = JobForm(job_id=job.id)
                
            
        context.update({'form' : form, 'action' : '/minhas-vagas/editar/' + job_id + '/'})
        return render(request, template, context)
    else:
        messages.error(request, u'Esta vaga foi criada a mais de 24 horas atrás. As vagas só podem ser editadas até 24 após sua criação. Por favor, considere excluí-la e criar uma nova.')
        return HttpResponseRedirect(reverse('colabre_web.views.my_jobs.index'))
"""
