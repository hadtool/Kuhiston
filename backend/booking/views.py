from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import BookingRequestForm
from .models import BookingObject, BookingRequest


def object_list(request):
    """Список активных объектов бронирования (с фильтром по месту)."""
    qs = BookingObject.objects.filter(is_active=True).select_related("category", "region").order_by("-is_promoted", "name_ru")
    place_id = request.GET.get("place")
    category = request.GET.get("category")
    place = None
    if place_id:
        from places.models import Place
        place = Place.objects.filter(pk=place_id).first()
        if place:
            qs = qs.filter(places__id=place.pk)
        else:
            qs = qs.none()
    if category:
        qs = qs.filter(category__code=category)
    return render(request, "booking/objects.html", {"objects": qs, "place": place})


def object_detail(request, pk):
    """Карточка объекта бронирования + форма заявки."""
    obj = get_object_or_404(
        BookingObject.objects.select_related("category", "region").prefetch_related("places"),
        pk=pk,
        is_active=True,
    )
    form = BookingRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request_obj = form.save(commit=False)
        request_obj.booking_object = obj
        if request.user.is_authenticated:
            request_obj.tourist = request.user
        request_obj.save()
        messages.success(request, _("Заявка отправлена! Владелец свяжется с вами."))
        return redirect("booking:object_detail", pk=obj.pk)
    return render(request, "booking/object_detail.html", {"object": obj, "form": form})


@login_required
def my_panel(request):
    """Личный кабинет владельца места: объекты и заявки на них."""
    objects = BookingObject.objects.filter(owner=request.user).select_related("category")
    own_ids = [o.pk for o in objects]
    requests = BookingRequest.objects.filter(booking_object__in=own_ids).select_related("booking_object") if own_ids else []
    return render(request, "booking/my_panel.html", {"my_objects": objects, "requests": requests})


@login_required
def set_status(request, pk, status):
    """Подтверждение/отклонение заявки владельцем."""
    req_obj = get_object_or_404(
        BookingRequest.objects.select_related("booking_object"),
        pk=pk,
        booking_object__owner=request.user,
    )
    if status in {"confirmed", "rejected"}:
        req_obj.status = status
        req_obj.save(update_fields=["status", "updated_at"])
        messages.success(request, _("Заявка: %s.") % req_obj.get_status_display().lower())
    return redirect("booking:my_panel")