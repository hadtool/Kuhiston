from django import forms
from django.utils.translation import gettext_lazy as _

from .models import BookingRequest


class BookingRequestForm(forms.ModelForm):
    """Форма заявки на бронирование (без онлайн-оплаты, PROJECT.md раздел 7)."""

    class Meta:
        model = BookingRequest
        fields = ["tourist_name", "tourist_contact", "check_in", "check_out", "notes", "pay_on_site"]
        widgets = {
            "tourist_name": forms.TextInput(attrs={"placeholder": _("Иван Иванов")}),
            "tourist_contact": forms.TextInput(attrs={"placeholder": _("Телефон или email")}),
            "check_in": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "check_out": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        if check_in and check_out and check_out < check_in:
            raise forms.ValidationError(_("Дата выезда не может быть раньше даты заезда."))
        return cleaned