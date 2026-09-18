from django import forms

from .models import Place


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Проверяет каждое из нескольких загруженных изображений."""

    def clean(self, data, initial=None):
        single_clean = super().clean
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [single_clean(item, initial) for item in data]


class VolunteerPlaceForm(forms.ModelForm):
    """Форма, через которую волонтёр отправляет место на модерацию."""

    photos = MultipleImageField(
        label="Фотографии",
        required=False,
        widget=MultipleFileInput(attrs={"accept": "image/*"}),
        help_text="Можно выбрать несколько фотографий.",
    )

    class Meta:
        model = Place
        fields = [
            "name_ru", "name_en", "name_tg",
            "description_ru", "description_en", "description_tg",
            "category", "latitude", "longitude", "region", "opening_hours",
            "entrance_fee", "access_difficulty", "recommended_seasons",
        ]
        widgets = {
            "description_ru": forms.Textarea(attrs={"rows": 4}),
            "description_en": forms.Textarea(attrs={"rows": 4}),
            "description_tg": forms.Textarea(attrs={"rows": 4}),
            "opening_hours": forms.Textarea(attrs={"rows": 2}),
            "recommended_seasons": forms.TextInput(
                attrs={"placeholder": '["весна", "осень"]'}
            ),
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Для корректной карточки места все три версии текста обязательны.
        for field_name in (
            "name_ru", "name_en", "name_tg",
            "description_ru", "description_en", "description_tg",
        ):
            self.fields[field_name].required = True

    def clean_latitude(self):
        value = self.cleaned_data["latitude"]
        if not -90 <= value <= 90:
            raise forms.ValidationError("Широта должна быть в диапазоне от −90 до 90.")
        return value

    def clean_longitude(self):
        value = self.cleaned_data["longitude"]
        if not -180 <= value <= 180:
            raise forms.ValidationError("Долгота должна быть в диапазоне от −180 до 180.")
        return value
