"""Views for companies app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.views import AdministratorRequiredMixin

from .forms import CompanyForm
from .models import Company


class CompanyListView(LoginRequiredMixin, AdministratorRequiredMixin, ListView):
    model = Company
    template_name = "companies/company_list.html"
    context_object_name = "companies"


class CompanyCreateView(LoginRequiredMixin, AdministratorRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:company_list")

    def form_valid(self, form):
        messages.success(self.request, "Company created successfully.")
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, AdministratorRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:company_list")

    def form_valid(self, form):
        messages.success(self.request, "Company updated successfully.")
        return super().form_valid(form)


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = "companies/company_detail.html"
    context_object_name = "company"
