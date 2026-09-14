from django.conf import settings
from django.db import models

from places.models import Place, Region


class Route(models.Model):
    """Курируемый готовый многодневный маршрут (PROJECT.md раздел 6, п. 2)."""

    class ModerationStatus(models.TextChoices):
        PENDING = "pending", "На проверке"
        PUBLISHED = "published", "Опубликовано"
        REJECTED = "rejected", "Отклонено"

    name_ru = models.CharField("Название (ru)", max_length=255)
    name_en = models.CharField("Название (en)", max_length=255)
    name_tg = models.CharField("Название (tg)", max_length=255)
    description_ru = models.TextField("Описание (ru)", blank=True)
    description_en = models.TextField("Описание (en)", blank=True)
    description_tg = models.TextField("Описание (tg)", blank=True)
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="routes",
        verbose_name="Регион",
    )
    duration_days = models.PositiveIntegerField("Количество дней", default=1)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="authored_routes", verbose_name="Автор",
    )
    moderation_status = models.CharField(
        "Статус модерации", max_length=20, choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    is_promoted = models.BooleanField("Продвижение в топе", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        ordering = ["-is_promoted", "-created_at"]

    def __str__(self):
        return f"{self.name_ru} — {self.duration_days} дн."

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", "") or self.name_ru

    def get_description(self, lang):
        return getattr(self, f"description_{lang}", "") or self.description_ru

    @property
    def stops_count(self):
        return self.stops.count()

    @property
    def total_km(self):
        total = 0.0
        ordered = list(self.stops.select_related("place").order_by("day", "order"))
        prev = None
        for s in ordered:
            if prev is not None:
                total += s.place.distance_to(prev.place)
            prev = s
        return round(total, 1)


class RouteStop(models.Model):
    """Точка маршрута: место + день + порядок + примерный тайминг."""

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="route_stops")
    day = models.PositiveIntegerField("День", default=1)
    order = models.PositiveIntegerField("Порядок в дне", default=0)
    minutes = models.PositiveIntegerField("Время (минуты)", blank=True, null=True)
    note = models.CharField("Заметка", max_length=255, blank=True)

    class Meta:
        verbose_name = "Точка маршрута"
        verbose_name_plural = "Точки маршрута"
        ordering = ["day", "order"]

    def __str__(self):
        return f"День {self.day}: {self.place}"