"""URL configuration for companies app."""

from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("", views.CompanyListView.as_view(), name="company_list"),
    path("create/", views.CompanyCreateView.as_view(), name="company_create"),
    path("<int:pk>/", views.CompanyDetailView.as_view(), name="company_detail"),
    path("<int:pk>/edit/", views.CompanyUpdateView.as_view(), name="company_update"),
]
