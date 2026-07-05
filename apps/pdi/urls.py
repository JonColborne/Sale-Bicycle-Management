"""URL configuration for PDI app."""

from django.urls import path

from . import views

app_name = "pdi"

urlpatterns = [
    path("templates/", views.PDITemplateListView.as_view(), name="template_list"),
    path("inspections/", views.PDIInspectionListView.as_view(), name="inspection_list"),
    path("inspections/<int:pk>/", views.PDIInspectionDetailView.as_view(), name="inspection_detail"),
    path("start/<int:vehicle_pk>/", views.PDIStartView.as_view(), name="pdi_start"),
    path("items/<int:pk>/", views.PDIItemUpdateView.as_view(), name="item_update"),
    path("inspections/<int:pk>/complete/", views.PDICompleteView.as_view(), name="inspection_complete"),
    path("inspections/<int:inspection_pk>/sign-off/", views.PDISignOffView.as_view(), name="sign_off"),
]
