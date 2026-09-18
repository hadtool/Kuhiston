import math

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from kuhiston.routing import haversine_km, osrm_route

from .models import Place, PlaceCategory, Region, Review
from .serializers import (
    PlaceCategorySerializer,
    PlaceDetailSerializer,
    PlaceListSerializer,
    RegionSerializer,
    ReviewSerializer,
    SimpleRoutePointSerializer,
)


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
            # Платное продвижение (Этап 7): продвинутые места всегда в топе выдачи.
            places.sort(key=lambda p: (not p.is_promoted, p.distance_km))
        else:
            for p in places:
                p.distance_km = None
        serializer = PlaceListSerializer(places, many=True, context=self.get_serializer_context())
        return Response(serializer.data)


class PlaceDetailView(generics.RetrieveAPIView):
    # Заявки волонтёров со статусом pending/rejected не должны раскрываться
    # через прямой URL до решения модератора.
    queryset = Place.objects.filter(moderation_status="published").select_related("category", "region").prefetch_related("photos")
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


class SimpleRouteView(APIView):
    """Простой маршрут: список и маршрут из N ближайших мест от точки отправителя.

    Query: lat, lng (обязательны), limit (до 10, по умолчанию 5).
    Возвращает точки, отсортированные по расстоянию от старта,
    расстояние «по воздуху» от предыдущей точки и суммарную дистанцию (в км).
    """

    def get_serializer_context(self):
        return {"language": getattr(self.request, "LANGUAGE_CODE", "ru")}

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            return Response({"error": "lat and lng are required"}, status=400)
        try:
            lat_f, lng_f = float(lat), float(lng)
            limit = min(max(int(request.query_params.get("limit", 5)), 1), 10)
        except ValueError:
            return Response({"error": "invalid lat/lng/limit"}, status=400)

        places = list(Place.objects.select_related("category", "region").filter(moderation_status="published"))
        for p in places:
            p.distance_from_start_km = round(haversine(lat_f, lng_f, float(p.latitude), float(p.longitude)), 1)
        places.sort(key=lambda p: p.distance_from_start_km)
        places = places[:limit]

        total = 0.0
        prev = (lat_f, lng_f)
        for p in places:
            p.leg_km = round(haversine(prev[0], prev[1], float(p.latitude), float(p.longitude)), 1)
            total += p.leg_km
            prev = (float(p.latitude), float(p.longitude))

        serializer = SimpleRoutePointSerializer(places, many=True, context=self.get_serializer_context())
        return Response(
            {
                "start": {"lat": lat_f, "lng": lng_f},
                "limit": limit,
                "count": len(serializer.data),
                "total_km": round(total, 1),
                "points": serializer.data,
            }
        )


class PlaceReviewsView(APIView):
    """Отзывы к месту: список (GET) и создание/обновление (POST, только для авторизованных)."""

    def get_place(self, pk):
        try:
            return Place.objects.get(pk=pk, moderation_status="published")
        except Place.DoesNotExist:
            return None

    def get(self, request, pk):
        place = self.get_place(pk)
        if not place:
            return Response(status=404)
        reviews = list(Review.objects.filter(place=place).select_related("author")[:20])
        data = ReviewSerializer(reviews, many=True, context={"request": request}).data
        avg = place.average_rating
        my_review = None
        if request.user.is_authenticated:
            obj = Review.objects.filter(place=place, author=request.user).first()
            my_review = ReviewSerializer(obj, context={"request": request}).data if obj else None
        return Response({"average": avg, "count": place.reviews_count, "reviews": data, "my_review": my_review})

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        place = self.get_place(pk)
        if not place:
            return Response(status=404)
        try:
            rating = int(request.data.get("rating", 0))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid rating"}, status=400)
        if rating < 1 or rating > 5:
            return Response({"detail": "Rating must be 1–5"}, status=400)
        obj, _ = Review.objects.update_or_create(
            place=place,
            author=request.user,
            defaults={"rating": rating, "text": request.data.get("text", "")},
        )
        return Response(ReviewSerializer(obj, context={"request": request}).data, status=201)


class OfflineRegionsView(generics.ListAPIView):
    """Список регионов для офлайн-скачивания (Этап 6)."""

    queryset = Region.objects.prefetch_related("places")
    serializer_class = RegionSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["language"] = getattr(self.request, "LANGUAGE_CODE", "ru")
        return ctx


class OfflineRegionBundleView(APIView):
    """Офлайн-бандл региона: сам регион, границы и все опубликованные места (с фото)."""

    def get(self, request, pk):
        region = Region.objects.filter(pk=pk).prefetch_related("places").first()
        if not region:
            return Response(status=404)
        language = getattr(request, "LANGUAGE_CODE", "ru")
        places = list(region.places.filter(moderation_status="published").select_related("category", "region").prefetch_related("photos"))
        for p in places:
            p.distance_km = None
        data = PlaceDetailSerializer(places, many=True, context={"request": request, "language": language}).data
        bounds = None
        if places:
            bounds = {
                "lat_min": min(float(p.latitude) for p in places),
                "lat_max": max(float(p.latitude) for p in places),
                "lng_min": min(float(p.longitude) for p in places),
                "lng_max": max(float(p.longitude) for p in places),
            }
        return Response(
            {
                "region": RegionSerializer(region, context={"language": language}).data,
                "bounds": bounds,
                "count": len(data),
                "places": data,
            }
        )


class NavigationRouteView(APIView):
    """Маршрут по дорогам/тропам от точки отправления до точки назначения.

    Query: start=lat,lng, end=lat,lng, profile (driving|foot|bike, по умолчанию driving).
    Ответ содержит distance_km, duration_min, geometry (GeoJSON LineString) и
    source ("osrm" — маршрут по OSM-данным, "fallback" — по прямой, если OSRM недоступен).
    """

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            return Response({"error": "start and end (lat,lng) are required"}, status=400)
        try:
            s = tuple(float(x) for x in start.split(","))
            e = tuple(float(x) for x in end.split(","))
            if len(s) != 2 or len(e) != 2:
                raise ValueError
        except ValueError:
            return Response({"error": "invalid start/end coordinates"}, status=400)

        profile = request.query_params.get("profile", "driving")
        return Response(osrm_route(s, e, profile))
