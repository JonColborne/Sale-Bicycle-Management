"""Reports views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Sum
from django.views.generic import TemplateView

from apps.vehicles.models import DriveType, Vehicle, VehicleStatus


class ReportBaseView(LoginRequiredMixin, TemplateView):
    """Base class for report views."""

    def get_base_queryset(self):
        qs = Vehicle.objects.all()
        user = self.request.user
        if not user.is_administrator and user.company:
            qs = qs.filter(company=user.company)
        return qs


class InventoryReportView(ReportBaseView):
    template_name = "reports/inventory_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_base_queryset().select_related("company").order_by("company", "vehicle_type", "manufacturer")
        ctx["vehicles"] = qs
        ctx["total"] = qs.count()
        ctx["by_type"] = qs.values("vehicle_type").annotate(count=Count("id")).order_by("vehicle_type")
        ctx["by_status"] = qs.values("status").annotate(count=Count("id")).order_by("status")
        return ctx


class PDIStatusReportView(ReportBaseView):
    template_name = "reports/pdi_status_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_base_queryset()
        ctx["awaiting"] = qs.filter(status=VehicleStatus.AWAITING_INSPECTION).select_related("company")
        ctx["in_progress"] = qs.filter(status=VehicleStatus.PDI_IN_PROGRESS).select_related("company")
        ctx["completed"] = qs.filter(status=VehicleStatus.READY_FOR_SALE).select_related("company")
        return ctx


class ValuationReportView(ReportBaseView):
    template_name = "reports/valuation_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_base_queryset().exclude(status=VehicleStatus.ARCHIVED)
        stats = qs.aggregate(
            total_purchase=Sum("purchase_cost"),
            total_rrp=Sum("recommended_retail_price"),
            count=Count("id"),
        )
        ctx.update(stats)
        ctx["vehicles"] = qs.select_related("company").order_by("company", "stock_number")
        return ctx


class MarginReportView(ReportBaseView):
    template_name = "reports/margin_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = (
            self.get_base_queryset()
            .filter(status=VehicleStatus.SOLD)
            .select_related("company")
            .order_by("-actual_sale_price")
        )
        stats = qs.aggregate(
            total_sales=Sum("actual_sale_price"),
            total_cost=Sum("purchase_cost"),
        )
        total_sales = stats["total_sales"] or 0
        total_cost = stats["total_cost"] or 0
        ctx["vehicles"] = qs
        ctx["total_sales"] = total_sales
        ctx["total_cost"] = total_cost
        ctx["total_margin"] = total_sales - total_cost
        return ctx


class EBikeReportView(ReportBaseView):
    template_name = "reports/ebike_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = (
            self.get_base_queryset()
            .filter(drive_type=DriveType.ELECTRICALLY_ASSISTED)
            .select_related("company", "electric_detail")
            .order_by("company", "stock_number")
        )
        ctx["vehicles"] = qs
        ctx["total"] = qs.count()
        return ctx
