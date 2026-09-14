import math

from rest_framework import generics
from rest_framework.response import Response

from .models import Place, PlaceCategory
from .serializers import PlaceCategorySerializer, PlaceDetailSerializer, PlaceListSerializer


def haversine(lat1, lng1, lat2, lng2):
    """Возвращает расстояние в км между двумя точками."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class PlaceListView(generics.ListAPIView):
    """Список опубликованных мест.

    Параметры: lat, lng (для расстояния и сортировки), category (код категории).
    """

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx

    def get_queryset(self):
        qs = Place.objects.select_related("category", "region").filter(moderation_status="published")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__code=category)
        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        places = list(qs)
        if lat and lng:
            lat_f, lng_f = float(lat), float(lng)
            for p in places:
                p.distance_km = round(haversine(lat_f, lng_f, float(p.latitude), float(p.longitude)), 1)
            places.sort(key=lambda p: p.distance_km)
        else:
            for p in places:
                p.distance_km = None
        serializer = PlaceListSerializer(places, many=True, context=self.get_serializer_context())
        return Response(serializer.data)


class PlaceDetailView(generics.RetrieveAPIView):
    queryset = Place.objects.select_related("category", "region").prefetch_related("photos")
    serializer_class = PlaceDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx

    def get_object(self):
        obj = super().get_object()
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")
        obj.distance_km = None
        if lat and lng:
            obj.distance_km = round(haversine(float(lat), float(lng), float(obj.latitude), float(obj.longitude)), 1)
        return obj


class CategoryListView(generics.ListAPIView):
    queryset = PlaceCategory.objects.order_by("position", "name_ru")
    serializer_class = PlaceCategorySerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx