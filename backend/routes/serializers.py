from rest_framework import serializers

from .models import Route, RouteStop


class RouteListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ["id", "name", "description", "region", "duration_days", "stops_count", "is_promoted"]

    def get_name(self, obj):
        return obj.get_name(self.context["language"])

    def get_description(self, obj):
        return obj.get_description(self.context["language"])

    def get_region(self, obj):
        return obj.region.get_name(self.context["language"]) if obj.region_id else None


class RouteStopSerializer(serializers.ModelSerializer):
    place_id = serializers.IntegerField(source="place.id")
    place_name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = RouteStop
        fields = ["id", "place_id", "place_name", "category", "lat", "lng", "minutes", "note"]

    def get_place_name(self, obj):
        return obj.place.get_name(self.context["language"])

    def get_category(self, obj):
        return obj.place.category.get_name(self.context["language"]) if obj.place.category_id else None

    def get_lat(self, obj):
        return float(obj.place.latitude)

    def get_lng(self, obj):
        return float(obj.place.longitude)


class RouteDetailSerializer(RouteListSerializer):
    days = serializers.SerializerMethodField()

    class Meta(RouteListSerializer.Meta):
        fields = RouteListSerializer.Meta.fields + ["days"]

    def get_days(self, obj):
        stops = obj.stops.select_related("place", "place__category").order_by("day", "order")
        grouped = {}
        for stop in stops:
            grouped.setdefault(stop.day, []).append(RouteStopSerializer(stop, context=self.context).data)
        return [{"day": day, "stops": grouped[day]} for day in sorted(grouped)]