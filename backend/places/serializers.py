from rest_framework import serializers

from .models import Place, PlaceCategory, PlacePhoto


class PlaceCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = PlaceCategory
        fields = ["code", "name"]

    def get_name(self, obj):
        return obj.get_name(self.context["language"])


class PlacePhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()

    class Meta:
        model = PlacePhoto
        fields = ["id", "url", "caption", "sort_order"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image and obj.image.name:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_caption(self, obj):
        lang = self.context["language"]
        return getattr(obj, f"caption_{lang}", "") or obj.caption_ru


class PlaceListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    rating = serializers.FloatField(source="average_rating", read_only=True)

    class Meta:
        model = Place
        fields = ["id", "name", "category", "lat", "lng", "distance_km", "rating"]

    def get_name(self, obj):
        return obj.get_name(self.context["language"])

    def get_category(self, obj):
        return obj.category.get_name(self.context["language"])

    def get_lat(self, obj):
        return float(obj.latitude)

    def get_lng(self, obj):
        return float(obj.longitude)

    def get_distance_km(self, obj):
        return obj.distance_km  # атрибут-аннотация, если передана точка


class PlaceDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    rating = serializers.FloatField(source="average_rating", read_only=True)
    access_difficulty = serializers.SerializerMethodField()
    photos = PlacePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "description",
            "category",
            "region",
            "lat",
            "lng",
            "opening_hours",
            "entrance_fee",
            "recommended_seasons",
            "access_difficulty",
            "rating",
            "reviews_count",
            "distance_km",
            "photos",
        ]

    def get_name(self, obj):
        return obj.get_name(self.context["language"])

    def get_description(self, obj):
        return obj.get_description(self.context["language"])

    def get_category(self, obj):
        return obj.category.get_name(self.context["language"])

    def get_region(self, obj):
        return obj.region.get_name(self.context["language"])

    def get_lat(self, obj):
        return float(obj.latitude)

    def get_lng(self, obj):
        return float(obj.longitude)

    def get_distance_km(self, obj):
        return obj.distance_km

    def get_access_difficulty(self, obj):
        return obj.get_access_difficulty_display()


class SimpleRoutePointSerializer(serializers.ModelSerializer):
    """Точка простого маршрута: расстояние от старта и между соседними точками."""

    name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    distance_from_start_km = serializers.SerializerMethodField()
    leg_km = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ["id", "name", "category", "lat", "lng", "distance_from_start_km", "leg_km"]

    def get_name(self, obj):
        return obj.get_name(self.context["language"])

    def get_category(self, obj):
        return obj.category.get_name(self.context["language"])

    def get_lat(self, obj):
        return float(obj.latitude)

    def get_lng(self, obj):
        return float(obj.longitude)

    def get_distance_from_start_km(self, obj):
        return getattr(obj, "distance_from_start_km", None)

    def get_leg_km(self, obj):
        return getattr(obj, "leg_km", None)