"""REST API for PDI app."""

from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import PDIInspection, PDITemplate


class PDITemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDITemplate
        fields = "__all__"


class PDIInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDIInspection
        fields = "__all__"
        read_only_fields = ["started_at"]


class PDITemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PDITemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PDITemplate.objects.filter(is_active=True).prefetch_related("items")


class PDIInspectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PDIInspectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = PDIInspection.objects.select_related("vehicle", "technician")
        user = self.request.user
        if not user.is_administrator:
            qs = qs.filter(vehicle__company=user.company)
        return qs
