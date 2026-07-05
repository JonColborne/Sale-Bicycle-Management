"""URL configuration for vehicles app."""

from django.urls import path

from . import views

app_name = "vehicles"

urlpatterns = [
    path("", views.VehicleListView.as_view(), name="vehicle_list"),
    path("create/", views.VehicleCreateView.as_view(), name="vehicle_create"),
    path("<int:pk>/", views.VehicleDetailView.as_view(), name="vehicle_detail"),
    path("<int:pk>/edit/", views.VehicleUpdateView.as_view(), name="vehicle_update"),
    path("<int:pk>/status/", views.VehicleStatusUpdateView.as_view(), name="vehicle_status"),
    path("<int:pk>/electric/", views.ElectricDetailUpdateView.as_view(), name="vehicle_electric"),
    path("<int:pk>/assessment/", views.UsedAssessmentUpdateView.as_view(), name="vehicle_assessment"),
]
