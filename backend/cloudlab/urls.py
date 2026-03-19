"""
URL configuration for cloudlab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a  to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

PROJECT_ROOT = settings.BASE_DIR.parent

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('landing.html', TemplateView.as_view(template_name='landing.html'), name='landing-html'),
    path('index.html', TemplateView.as_view(template_name='index.html'), name='index-html'),
    path('skills.html', TemplateView.as_view(template_name='skills.html'), name='skills-html'),
    path('projects.html', TemplateView.as_view(template_name='projects.html'), name='projects-html'),
    path('experiments.html', TemplateView.as_view(template_name='experiments.html'), name='experiments-html'),
    path('contact.html', TemplateView.as_view(template_name='contact.html'), name='contact-html'),
    path('api-status/', TemplateView.as_view(template_name='homepage.html'), name='api-status'),
    path('assets/<path:path>', serve, {'document_root': str(PROJECT_ROOT / 'assets')}),
    path('styles/<path:path>', serve, {'document_root': str(PROJECT_ROOT / 'styles')}),
    path('scripts/<path:path>', serve, {'document_root': str(PROJECT_ROOT / 'scripts')}),
    path('config/<path:path>', serve, {'document_root': str(PROJECT_ROOT / 'config')}),
    # Use a custom admin URL path to help prevent automated bot scanning and brute-force attacks
    path('airlock/', admin.site.urls),
    path('api/', include('portfolioapi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
