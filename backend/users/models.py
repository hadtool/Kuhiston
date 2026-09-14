from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь с ролью в системе.

    Роли — по PROJECT.md раздел 3. Гость (незарегистрированный турист) моделью
    не описывается. Админ/основатель дополнительно использует is_superuser.
    """

    class Role(models.TextChoices):
        TOURIST = "tourist", "турист"
        VOLUNTEER = "volunteer", "волонтёр"
        PLACE_OWNER = "place_owner", "владелец места"
        ADMIN = "admin", "администратор"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TOURIST,
        verbose_name="роль",
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def is_volunteer(self):
        return self.role == self.Role.VOLUNTEER

    def is_place_owner(self):
        return self.role == self.Role.PLACE_OWNER

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser