from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from kuhiston.moderation import check_place

from .forms import VolunteerPlaceForm
from .models import Place, PlaceCategory, PlacePhoto


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
        "nav_transport": _("Способ передвижения"),
        "nav_driving": _("На автомобиле"),
        "nav_foot": _("Пешком"),
        "nav_bike": _("На велосипеде"),
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
        "offline_btn": _("Офлайн-режим"),
        "offline_hint": _("Скачайте карту и данные региона — они будут доступны без интернета."),
        "offline_download": _("Скачать"),
        "offline_downloading": _("Скачивание…"),
        "offline_saved_ok": _("Сохранено офлайн"),
        "offline_remove": _("Удалить"),
        "offline_cached": _("Доступно офлайн"),
        "offline_empty": _("Регионы не найдены"),
        "offline_places": _("мест(а)"),
        "promoted": _("Продвинутое"),
        "donate_btn": _("Поддержать проект"),
    }
    context = {
        "maptiler_api_key": settings.MAPTILER_API_KEY,
        "categories": categories,
        "js_strings": js_strings,
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, "home.html", context)


def donate(request):
    """Страница добровольных донатов (Этап 7)."""
    return render(request, "donate.html", {"donate_url": settings.DONATE_URL})


@login_required(login_url="users:login")
def volunteer_place_add(request):
    """Принимает заявку волонтёра и сохраняет её только для модерации."""
    if not request.user.is_volunteer():
        raise PermissionDenied("Добавлять места могут только волонтёры.")

    if request.method == "POST":
        form = VolunteerPlaceForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                place = form.save(commit=False)
                place.added_by = request.user
                place.moderation_status = Place.ModerationStatus.PENDING
                # Используем ту же проверку, что и в админке. Совпадение
                # запрещённых слов не публикуется и сразу уходит в rejected.
                forbidden_hits = check_place(place)
                if forbidden_hits:
                    place.moderation_status = Place.ModerationStatus.REJECTED
                place.save()
                for index, image in enumerate(request.FILES.getlist("photos")):
                    PlacePhoto.objects.create(place=place, image=image, sort_order=index)
            if forbidden_hits:
                messages.warning(request, "Заявка сохранена, но требует ручной проверки модератором.")
            else:
                messages.success(request, "Место отправлено на проверку.")
            return redirect("places:volunteer_place_add")
    else:
        form = VolunteerPlaceForm()
    return render(request, "places/volunteer_place_form.html", {"form": form})
