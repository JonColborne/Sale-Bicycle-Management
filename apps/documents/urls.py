"""URL configuration for documents app."""

from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("vehicle/<int:vehicle_pk>/upload/", views.DocumentUploadView.as_view(), name="document_upload"),
    path("<int:pk>/", views.DocumentDetailView.as_view(), name="document_detail"),
    path("<int:pk>/delete/", views.DocumentDeleteView.as_view(), name="document_delete"),
]
