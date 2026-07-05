"""URL configuration for reports app."""

from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("inventory/", views.InventoryReportView.as_view(), name="inventory"),
    path("pdi-status/", views.PDIStatusReportView.as_view(), name="pdi_status"),
    path("valuation/", views.ValuationReportView.as_view(), name="valuation"),
    path("margin/", views.MarginReportView.as_view(), name="margin"),
    path("ebike/", views.EBikeReportView.as_view(), name="ebike"),
]
