"""Main routing settings."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

admin.autodiscover()

# See https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="index.html")),
    url(r"", include("core.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
  urlpatterns += staticfiles_urlpatterns()
