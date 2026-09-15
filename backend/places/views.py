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
        "route_hint": _("Кликните по точке маршрута, чтобы открыть место"),
        "route_total": _("Итого"),
        "route_empty": _("Рядом не найдено мест"),
        "km": _("км"),
        "days": _("дн."),
        "points_noun": _("точек"),
        "day_label": _("День"),
        "min": _("мин"),
        "nav_btn": _("Построить маршрут"),
        "book_btn": _("Забронировать рядом"),
        "nav_distance": _("Расстояние"),
        "nav_duration": _("Время"),
        "nav_fallback": _("Маршрут по прямой (сервис недоступен)"),
        "reviews_title": _("Отзывы"),
        "reviews_empty": _("Пока нет отзывов"),
        "review_yours": _("Ваш отзыв"),
        "review_leave": _("Оставить отзыв"),
        "review_rating_label": _("Оценка"),
        "review_text_placeholder": _("Поделитесь впечатлениями…"),
        "review_submit": _("Отправить отзыв"),
        "review_logged_in_need": _("Войдите, чтобы оставить отзыв"),
        "review_saved": _("Спасибо! Отзыв сохранён"),
        "review_fail": _("Не удалось сохранить отзыв"),
    }
    context = {
        "maptiler_api_key": settings.MAPTILER_API_KEY,
        "categories": categories,
        "js_strings": js_strings,
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, "home.html", context)