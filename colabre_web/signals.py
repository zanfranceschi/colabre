import django.dispatch

job_form_before_instance_saved = django.dispatch.Signal(providing_args=["job"])