from django.contrib import admin

from kuhiston.moderation import check_route

from .models import Route, RouteStop


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    fields = ["place", "day", "order", "minutes", "note"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["name_ru", "duration_days", "region", "moderation_status", "is_promoted", "stops_count", "author"]
    list_filter = ["moderation_status", "is_promoted", "region"]
    search_fields = ["name_ru", "name_en", "name_tg", "description_ru"]
    list_editable = ["moderation_status", "is_promoted"]
    inlines = [RouteStopInline]
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["region", "author"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.author_id:
            obj.author = request.user
        if check_route(obj):
            obj.moderation_status = Route.ModerationStatus.REJECTED
        super().save_model(request, obj, form, change)


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ["route", "day", "order", "place", "minutes"]
    list_filter = ["route", "day"]
    autocomplete_fields = ["route", "place"]
    ordering = ["route", "day", "order"]