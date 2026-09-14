from django.contrib import admin

from .models import BookingCategory, BookingObject, BookingRequest


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


class BookingRequestInline(admin.TabularInline):
    model = BookingRequest
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ["booking_object", "tourist_name", "tourist_contact", "check_in", "check_out", "pay_on_site", "status", "created_at"]
    list_filter = ["status", "pay_on_site", "created_at"]
    list_editable = ["status"]
    search_fields = ["tourist_name", "tourist_contact", "booking_object__name_ru", "booking_object__name_en", "booking_object__name_tg"]
    autocomplete_fields = ["tourist"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]