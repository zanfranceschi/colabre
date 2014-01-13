import django.dispatch

job_form_before_instance_saved = django.dispatch.Signal(providing_args=["job"])
job_form_instance_saved = django.dispatch.Signal(providing_args=["job"])
applyforjob_form_message_sent = django.dispatch.Signal(providing_args=["job_id", "ip", "mail_uuid"])