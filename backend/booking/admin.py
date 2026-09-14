from django.contrib import admin

from .models import BookingCategory, BookingObject


@admin.register(BookingCategory)
class BookingCategoryAdmin(admin.ModelAdmin):
    list_display = ["name_ru", "name_en", "name_tg", "code", "position"]
    list_editable = ["position"]
    prepopulated_fields = {"code": ("name_ru",)}
    search_fields = ["name_ru", "name_en", "name_tg"]


@admin.register(BookingObject)
class BookingObjectAdmin(admin.ModelAdmin):
    list_display = [
        "name_ru",
        "category",
        "region",
        "owner",
        "is_active",
        "is_promoted",
        "created_at",
    ]
    list_filter = ["category", "region", "is_active", "is_promoted"]
    list_editable = ["is_active", "is_promoted"]
    search_fields = ["name_ru", "name_en", "name_tg", "phone", "email"]
    autocomplete_fields = ["owner"]
    filter_horizontal = ["places"]
    fieldsets = (
        ("Название", {"fields": ("name_ru", "name_en", "name_tg")}),
        ("Описание", {"fields": ("description_ru", "description_en", "description_tg")}),
        ("Классификация", {"fields": ("category", "region", "places")}),
        ("Координаты", {"fields": ("latitude", "longitude"), "classes": ("wide",)}),
        ("Контакты", {"fields": ("phone", "email", "website")}),
        ("Владелец и статус", {"fields": ("owner", "is_active", "is_promoted")}),
    )