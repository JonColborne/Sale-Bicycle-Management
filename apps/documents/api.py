"""REST API for documents app."""

from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import VehicleDocument


class VehicleDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    is_image = serializers.BooleanField(read_only=True)

    class Meta:
        model = VehicleDocument
        fields = [
            "id",
            "vehicle",
            "category",
            "title",
            "file",
            "file_url",
            "is_image",
            "description",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at", "uploaded_by"]

    def get_file_url(self, obj) -> str:
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return ""


class VehicleDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = VehicleDocument.objects.select_related("vehicle__company", "uploaded_by")
        user = self.request.user
        if not user.is_administrator:
            qs = qs.filter(vehicle__company=user.company)
        vehicle_id = self.request.query_params.get("vehicle")
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
