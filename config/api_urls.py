"""
REST API URL configuration for BSPCMS project.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api import UserViewSet
from apps.companies.api import CompanyViewSet
from apps.documents.api import VehicleDocumentViewSet
from apps.pdi.api import PDITemplateViewSet, PDIInspectionViewSet
from apps.reports.api import ReportViewSet
from apps.vehicles.api import VehicleViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"documents", VehicleDocumentViewSet, basename="document")
router.register(r"pdi/templates", PDITemplateViewSet, basename="pdi-template")
router.register(r"pdi/inspections", PDIInspectionViewSet, basename="pdi-inspection")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]
