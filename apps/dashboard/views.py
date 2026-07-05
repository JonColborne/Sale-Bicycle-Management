"""Dashboard views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import TemplateView
from django.utils import timezone

from apps.vehicles.models import Vehicle, VehicleStatus


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        qs = Vehicle.objects.all()
        if not user.is_administrator and user.company:
            qs = qs.filter(company=user.company)

        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stats = qs.aggregate(
            total_stock=Count("id"),
            total_purchase_value=Sum("purchase_cost"),
            total_rrp=Sum("recommended_retail_price"),
        )

        ctx.update(
            {
                "awaiting_inspection": qs.filter(status=VehicleStatus.AWAITING_INSPECTION).count(),
                "pdi_in_progress": qs.filter(status=VehicleStatus.PDI_IN_PROGRESS).count(),
                "ready_for_sale": qs.filter(status=VehicleStatus.READY_FOR_SALE).count(),
                "sold_this_month": qs.filter(
                    status=VehicleStatus.SOLD,
                    updated_at__gte=this_month_start,
                ).count(),
                "total_stock": stats["total_stock"] or 0,
                "stock_purchase_value": stats["total_purchase_value"] or 0,
                "potential_retail_value": stats["total_rrp"] or 0,
                "recent_vehicles": qs.select_related("company").order_by("-created_at")[:5],
            }
        )

        # Status breakdown
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        ctx["status_breakdown"] = [
            {"status": status, "label": label, "count": by_status.get(status, 0)}
            for status, label in VehicleStatus.choices
        ]

        return ctx
