from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Region(models.Model):
    """Территориальная единица Таджикистана.

    Нужна для офлайн-скачивания карт по регионам и организации волонтёров.
    """

    code = models.SlugField(max_length=40, unique=True, verbose_name="код")
    name_ru = models.CharField(max_length=120, verbose_name="название (ru)")
    name_en = models.CharField(max_length=120, verbose_name="название (en)")
    name_tg = models.CharField(max_length=120, verbose_name="название (tg)")
    position = models.PositiveSmallIntegerField(default=0, verbose_name="порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "name_ru"]
        verbose_name = "регион"
        verbose_name_plural = "регионы"

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", self.name_ru)

    def __str__(self):
        return self.name_ru


class PlaceCategory(models.Model):
    """Категория места: историческое, культурное, природное, религиозное и т.д.

    Расширяемый список — новые категории добавляются без изменения кода.
    """

    code = models.SlugField(max_length=40, unique=True, verbose_name="код")
    name_ru = models.CharField(max_length=80, verbose_name="название (ru)")
    name_en = models.CharField(max_length=80, verbose_name="название (en)")
    name_tg = models.CharField(max_length=80, verbose_name="название (tg)")
    position = models.PositiveSmallIntegerField(default=0, verbose_name="порядок сортировки")

    class Meta:
        ordering = ["position", "name_ru"]
        verbose_name = "категория места"
        verbose_name_plural = "категории мест"

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", self.name_ru)

    def __str__(self):
        return self.name_ru


class Place(models.Model):
    """Достопримечательность (культурная, историческая, природная и т.д.).

    Поля — по разделу 5 PROJECT.md. Мультиязычные тексты хранятся отдельными
    колонками на язык (ru/en/tg), координаты — десятичными градусами.
    """

    class AccessDifficulty(models.TextChoices):
        EASY_WALK = "easy_walk", "лёгкая пешая прогулка"
        NEED_OFFROAD = "need_offroad", "нужен внедорожник"
        MOUNTAIN_HIKE = "mountain_hike", "горный поход"
        OTHER = "other", "другое"

    class ModerationStatus(models.TextChoices):
        PENDING = "pending", "на проверке"
        PUBLISHED = "published", "опубликовано"
        REJECTED = "rejected", "отклонено"

    name_ru = models.CharField(max_length=200, verbose_name="название (ru)")
    name_en = models.CharField(max_length=200, verbose_name="название (en)")
    name_tg = models.CharField(max_length=200, verbose_name="название (tg)")

    description_ru = models.TextField(blank=True, verbose_name="описание (ru)")
    description_en = models.TextField(blank=True, verbose_name="описание (en)")
    description_tg = models.TextField(blank=True, verbose_name="описание (tg)")

    category = models.ForeignKey(
        PlaceCategory,
        on_delete=models.PROTECT,
        related_name="places",
        verbose_name="категория",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="places",
        verbose_name="регион",
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="долгота")

    opening_hours = models.TextField(blank=True, verbose_name="часы работы")
    entrance_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="входная цена, сомони"
    )
    access_difficulty = models.CharField(
        max_length=20,
        choices=AccessDifficulty.choices,
        default=AccessDifficulty.EASY_WALK,
        verbose_name="сложность доступа",
    )
    recommended_seasons = models.JSONField(
        default=list, blank=True, verbose_name="рекомендуемое время года"
    )

    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        verbose_name="статус модерации",
    )
    is_promoted = models.BooleanField(default=False, verbose_name="продвижение в топе (Этап 7)")
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_places",
        verbose_name="добавил (волонтёр)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_promoted", "name_ru"]
        verbose_name = "место"
        verbose_name_plural = "места"

    def get_name(self, lang):
        return getattr(self, f"name_{lang}", "") or self.name_ru

    def get_description(self, lang):
        return getattr(self, f"description_{lang}", "") or self.description_ru

    def get_coordinates(self):
        return (float(self.latitude), float(self.longitude))

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=models.Avg("rating"))["avg"]

    @property
    def reviews_count(self):
        return self.reviews.count()

    def distance_to(self, other):
        """Расстояние по прямой (хаверсин) до другого места, в км."""
        import math

        lat1, lng1 = self.get_coordinates()
        lat2, lng2 = other.get_coordinates()
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

    def __str__(self):
        return self.name_ru


class Review(models.Model):
    """Отзыв туриста о месте с оценкой 1–5.

    Автор — зарегистрированный пользователь (PROJECT.md раздел 3): регистрация
    нужна для отзывов. Отображение рейтинга на карточке — Этап 5.
    """

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="место",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
        verbose_name="автор",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="оценка (1–5)",
    )
    text = models.TextField(blank=True, verbose_name="текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            )
        ]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def __str__(self):
        return f"{self.place} — {self.rating}/5 ({self.author})"


class PlacePhoto(models.Model):
    """Фотографии места (несколько штук)."""

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="место",
    )
    image = models.ImageField(upload_to="places/%Y/%m/", verbose_name="файл")
    caption_ru = models.CharField(max_length=300, blank=True, verbose_name="подпись (ru)")
    caption_en = models.CharField(max_length=300, blank=True, verbose_name="подпись (en)")
    caption_tg = models.CharField(max_length=300, blank=True, verbose_name="подпись (tg)")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="порядок")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "фотография места"
        verbose_name_plural = "фотографии мест"

    def __str__(self):
        return f"{self.place} — фото #{self.pk}"