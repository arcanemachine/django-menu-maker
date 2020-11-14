from django.urls import reverse

from .constants import PROJECT_NAME


def project_name(request):
    return {'PROJECT_NAME': PROJECT_NAME}


def common_urls(request):
    return {'user_login_url': reverse('users:login'),
            'user_register_url': reverse('users:register')}
