"""Main routing settings."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()

# See https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = [
    url(r"", include("core.urls")),
    url(r"^login/$", "django.contrib.auth.views.login",
        {"template_name": "login.html.tmpl"}),
    url(r"^logout/$", "django.contrib.auth.views.logout"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^i18n/", include("django.conf.urls.i18n")),
]


# static() is a helper function to return a URL pattern for serving files in
# debug mode. If not in debug mode, this is a no-op.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
