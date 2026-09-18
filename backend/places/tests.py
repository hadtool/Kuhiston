from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import Place, PlaceCategory, Region


class VolunteerPlaceAddTests(TestCase):
    def setUp(self):
        self.category = PlaceCategory.objects.create(
            code="historical", name_ru="Историческое", name_en="Historical", name_tg="Таърихӣ"
        )
        self.region = Region.objects.create(
            code="sugd", name_ru="Согд", name_en="Sughd", name_tg="Суғд"
        )
        self.volunteer = User.objects.create_user(
            username="test-volunteer", password="safe-pass-123", role=User.Role.VOLUNTEER
        )
        self.tourist = User.objects.create_user(
            username="test-tourist", password="safe-pass-123", role=User.Role.TOURIST
        )

    def payload(self):
        return {
            "name_ru": "Тестовая крепость", "name_en": "Test Fortress", "name_tg": "Қалъаи санҷишӣ",
            "description_ru": "Историческое место для проверки формы.",
            "description_en": "Historic site for checking the form.",
            "description_tg": "Макони таърихӣ барои санҷиши шакл.",
            "category": self.category.pk, "region": self.region.pk,
            "latitude": "39.500000", "longitude": "67.600000",
            "opening_hours": "09:00–18:00", "entrance_fee": "25.00",
            "access_difficulty": Place.AccessDifficulty.EASY_WALK,
            "recommended_seasons": '["весна", "осень"]',
        }

    def test_only_volunteer_can_open_form(self):
        url = reverse("places:volunteer_place_add")
        response = self.client.get(url)
        self.assertRedirects(response, f"/users/login/?next={url}")
        self.client.login(username="test-tourist", password="safe-pass-123")
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_volunteer_submission_creates_pending_place_with_photo(self):
        self.client.login(username="test-volunteer", password="safe-pass-123")
        photo = SimpleUploadedFile(
            "fortress.gif",
            b"GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )
        response = self.client.post(reverse("places:volunteer_place_add"), {**self.payload(), "photos": photo})
        self.assertRedirects(response, reverse("places:volunteer_place_add"))
        place = Place.objects.get(name_ru="Тестовая крепость")
        self.assertEqual(place.added_by, self.volunteer)
        self.assertEqual(place.moderation_status, Place.ModerationStatus.PENDING)
        self.assertEqual(place.photos.count(), 1)

    def test_forbidden_content_is_not_published(self):
        self.client.login(username="test-volunteer", password="safe-pass-123")
        payload = self.payload()
        payload["name_ru"] = "Обманная крепость"
        self.client.post(reverse("places:volunteer_place_add"), payload)
        place = Place.objects.get(name_ru="Обманная крепость")
        self.assertEqual(place.moderation_status, Place.ModerationStatus.REJECTED)

    def test_pending_submission_is_not_available_in_tourist_api(self):
        self.client.login(username="test-volunteer", password="safe-pass-123")
        self.client.post(reverse("places:volunteer_place_add"), self.payload())
        place = Place.objects.get(name_ru="Тестовая крепость")
        self.client.logout()
        self.assertEqual(self.client.get(f"/api/places/{place.pk}/").status_code, 404)
