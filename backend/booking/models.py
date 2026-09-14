from django.conf import settings
from django.db import models


class BookingCategory(models.Model):
    """Категория объекта бронирования: жильё, гид, транспорт, ресторан и т.д.

    Расширяемый список — новые категории добавляются без изменения кода.
    """

    code = models.SlugField(max_length=40, unique=True, verbose_name="код")
    name_ru = models.CharField(max_length=80, verbose_name="название (ru)")
    name_en = models.CharField(max_length=80, verbose_name="название (en)")
    name_tg = models.CharField(max_length=80, verbose_name="название (tg)")
    position = models.PositiveSmallIntegerField(default=0, verbose_name="порядок сортировки")

    class Meta:
        ordering = ["position", "name_ru"]
        verbose_name = "категория объекта бронирования"
        verbose_name_plural = "категории объектов бронирования"

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", self.name_ru)

    def __str__(self):
        return self.name_ru


class BookingObject(models.Model):
    """Объект бронирования: гостевой дом/отель, гид, транспорт, ресторан.

    Связан с местами (достопримечательностями) через M2M — один объект может
    обслуживать несколько мест. Категории — по PROJECT.md раздел 7.
    """

    name_ru = models.CharField(max_length=200, verbose_name="название (ru)")
    name_en = models.CharField(max_length=200, verbose_name="название (en)")
    name_tg = models.CharField(max_length=200, verbose_name="название (tg)")
    description_ru = models.TextField(blank=True, verbose_name="описание (ru)")
    description_en = models.TextField(blank=True, verbose_name="описание (en)")
    description_tg = models.TextField(blank=True, verbose_name="описание (tg)")

    category = models.ForeignKey(
        BookingCategory,
        on_delete=models.PROTECT,
        related_name="booking_objects",
        verbose_name="категория",
    )
    places = models.ManyToManyField(
        "places.Place",
        related_name="booking_objects",
        verbose_name="связанные места",
        blank=True,
    )
    region = models.ForeignKey(
        "places.Region",
        on_delete=models.PROTECT,
        related_name="booking_objects",
        verbose_name="регион",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_booking_objects",
        verbose_name="владелец",
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="долгота")

    phone = models.CharField(max_length=40, blank=True, verbose_name="телефон")
    email = models.EmailField(blank=True, verbose_name="email")
    website = models.URLField(blank=True, verbose_name="сайт")

    is_active = models.BooleanField(default=True, verbose_name="активен")
    is_promoted = models.BooleanField(default=False, verbose_name="продвижение в топе")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_promoted", "name_ru"]
        verbose_name = "объект бронирования"
        verbose_name_plural = "объекты бронирования"

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", "") or self.name_ru

    def get_description(self, lang):
        return getattr(self, f"description_{lang}", "") or self.description_ru

    def get_coordinates(self):
        return (float(self.latitude), float(self.longitude))

    def __str__(self):
        return self.name_ru


class BookingRequest(models.Model):
    """Заявка на бронирование без онлайн-оплаты (PROJECT.md раздел 7).

    Турист оставляет заявку (даты, контакты), владелец объекта подтверждает или
    отклоняет её вручную. Онлайн-оплата — вне MVP.
    """

    class Status(models.TextChoices):
        NEW = "new", "новая"
        CONFIRMED = "confirmed", "подтверждена"
        REJECTED = "rejected", "отклонена"
        CANCELLED = "cancelled", "отменена туристом"

    booking_object = models.ForeignKey(
        BookingObject,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="объект бронирования",
    )
    tourist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_requests",
        verbose_name="турист",
    )
    tourist_name = models.CharField(max_length=200, verbose_name="имя туриста")
    tourist_contact = models.CharField(max_length=200, verbose_name="контакт туриста (телефон/email)")
    check_in = models.DateField(null=True, blank=True, verbose_name="дата заезда")
    check_out = models.DateField(null=True, blank=True, verbose_name="дата выезда")
    notes = models.TextField(blank=True, verbose_name="комментарий")
    pay_on_site = models.BooleanField(default=False, verbose_name="оплата на месте")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="статус",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заявка на бронирование"
        verbose_name_plural = "заявки на бронирование"

    def __str__(self):
        return f"{self.booking_object} — {self.tourist_name} ({self.get_status_display()})"