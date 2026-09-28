"""
URLs principais do IntegraOCI standalone.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from core.api import api_auth
from BpaApac.api import api_bpa_apac

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação (login, refresh, user info)
    path("api/v1/auth/", api_auth.urls),
    # Módulo IntegraOCI (BPA/APAC, combos OCI, auditoria)
    path("api/v1/bpa-apac/", api_bpa_apac.urls),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico"))),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
