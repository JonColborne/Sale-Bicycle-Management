"""Views for documents app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, View

from apps.audit.models import AuditLog
from apps.vehicles.models import Vehicle

from .forms import VehicleDocumentForm
from .models import VehicleDocument


class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = VehicleDocument
    form_class = VehicleDocumentForm
    template_name = "documents/document_upload.html"

    def get_vehicle(self):
        return get_object_or_404(Vehicle, pk=self.kwargs["vehicle_pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehicle"] = self.get_vehicle()
        return ctx

    def form_valid(self, form):
        vehicle = self.get_vehicle()
        form.instance.vehicle = vehicle
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        AuditLog.log(
            user=self.request.user,
            action="document_upload",
            instance=vehicle,
            description=f"Document '{self.object.title}' uploaded ({self.object.category})",
        )
        messages.success(self.request, "Document uploaded successfully.")
        return response

    def get_success_url(self):
        return reverse("vehicles:vehicle_detail", kwargs={"pk": self.kwargs["vehicle_pk"]})


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = VehicleDocument
    template_name = "documents/document_detail.html"
    context_object_name = "document"


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = VehicleDocument
    template_name = "documents/document_confirm_delete.html"

    def get_success_url(self):
        return reverse("vehicles:vehicle_detail", kwargs={"pk": self.object.vehicle.pk})

    def form_valid(self, form):
        vehicle = self.object.vehicle
        doc_title = self.object.title
        response = super().form_valid(form)
        AuditLog.log(
            user=self.request.user,
            action="document_delete",
            instance=vehicle,
            description=f"Document '{doc_title}' deleted",
        )
        messages.success(self.request, "Document deleted.")
        return response
