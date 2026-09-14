from django.contrib import admin

from . import models


class PlacePhotoInline(admin.TabularInline):
    model = models.PlacePhoto
    extra = 1


class ReviewInline(admin.TabularInline):
    model = models.Review
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name_ru", "name_en", "name_tg", "code", "position"]
    list_editable = ["position"]
    prepopulated_fields = {"code": ("name_ru",)}
    search_fields = ["name_ru", "name_en", "name_tg"]


@admin.register(models.PlaceCategory)
class PlaceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name_ru", "name_en", "name_tg", "code", "position"]
    list_editable = ["position"]
    prepopulated_fields = {"code": ("name_ru",)}
    search_fields = ["name_ru", "name_en", "name_tg"]


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        "name_ru",
        "category",
        "region",
        "moderation_status",
        "get_coordinates",
        "added_by",
        "created_at",
    ]
    list_filter = ["category", "region", "moderation_status", "access_difficulty"]
    list_editable = ["moderation_status"]
    search_fields = ["name_ru", "name_en", "name_tg", "description_ru", "description_en", "description_tg"]
    autocomplete_fields = ["added_by"]
    date_hierarchy = "created_at"
    inlines = [PlacePhotoInline, ReviewInline]
    fieldsets = (
        ("Название", {"fields": ("name_ru", "name_en", "name_tg")}),
        ("Описание", {"fields": ("description_ru", "description_en", "description_tg")}),
        ("Классификация", {"fields": ("category", "region")}),
        ("Координаты", {"fields": ("latitude", "longitude"), "classes": ("wide",)}),
        ("Доступность", {"fields": ("opening_hours", "entrance_fee", "access_difficulty", "recommended_seasons")}),
        ("Модерация", {"fields": ("moderation_status", "added_by")}),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.added_by_id:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.PlacePhoto)
class PlacePhotoAdmin(admin.ModelAdmin):
    list_display = ["place", "image", "sort_order", "uploaded_at"]
    list_editable = ["sort_order"]
    search_fields = ["place__name_ru", "place__name_en", "place__name_tg"]


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["place", "author", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    list_editable = ["rating"]
    search_fields = ["text", "place__name_ru", "place__name_en", "place__name_tg", "author__username"]
    autocomplete_fields = ["author"]
    readonly_fields = ["created_at", "updated_at"]