from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext as _

from .models import PlaceCategory


def home(request):
    """Главная страница: карта MapTiler + фильтр по категориям.

    Места подгружаются на фронтенде по API (задача «ближайшие места»).
    Здесь только категории для фильтра и API-ключ карты.
    """
    lang = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    categories = [
        {
            "code": c.code,
            "name": c.get_name(lang),
        }
        for c in PlaceCategory.objects.order_by("position")
    ]
    js_strings = {
        "locate": _("Определить моё местоположение"),
        "point_hint": _("Точка выбрана — нажмите ещё раз, чтобы убрать"),
        "loading": _("Загрузка…"),
        "no_places": _("Рядом пока нет мест"),
        "request_error": _("Не удалось получить данные"),
        "close": _("Закрыть"),
        "difficulty": _("Сложность доступа"),
        "hours": _("Часы работы"),
        "fee": _("Входная цена"),
        "seasons": _("Рекомендуемое время"),
        "region": _("Регион"),
        "currency": _("сомони"),
    }
    context = {
        "maptiler_api_key": settings.MAPTILER_API_KEY,
        "categories": categories,
        "js_strings": js_strings,
    }
    return render(request, "home.html", context)