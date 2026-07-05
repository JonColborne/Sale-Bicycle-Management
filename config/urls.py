"""
URL configuration for BSPCMS project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/dashboard/", permanent=False), name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("companies/", include("apps.companies.urls")),
    path("vehicles/", include("apps.vehicles.urls")),
    path("documents/", include("apps.documents.urls")),
    path("pdi/", include("apps.pdi.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("reports/", include("apps.reports.urls")),
    # REST API
    path("api/v1/", include("config.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
