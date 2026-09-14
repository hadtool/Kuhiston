from rest_framework import generics

from .models import Route
from .serializers import RouteDetailSerializer, RouteListSerializer


class RouteListView(generics.ListAPIView):
    """Список опубликованных многодневных маршрутов."""

    serializer_class = RouteListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx

    def get_queryset(self):
        qs = Route.objects.filter(moderation_status="published").select_related("region")
        region = self.request.query_params.get("region")
        if region:
            qs = qs.filter(region__code=region)
        return qs


class RouteDetailView(generics.RetrieveAPIView):
    """Детали маршрута с остановками, сгруппированными по дням."""

    queryset = Route.objects.filter(moderation_status="published").select_related("region")
    serializer_class = RouteDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx