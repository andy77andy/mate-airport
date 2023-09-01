from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from airlines.models import Airport, Route, Flight, Airplane, AirplaneType, Crew
from airlines.serializers import (
    FlightListSerializer,
    AirportDetailSerializer,
    CrewSerializer,
)

CREW_URL = reverse("airlines:crew-list")


def detail_url(crew_id: int):
    return reverse("airlines:crew-detail", args=[crew_id])


def sample_crew(**params):
    defaults = {
        "first_name": "Jennis",
        "last_name": "Joplin",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class CrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test1.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        crew = sample_crew()

        response = self.client.get(CREW_URL)
        crew = Crew.objects.all()
        serializer = CrewSerializer(crew, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_crew_with_image(self):
        crew = sample_crew()
        payload = {
            "first_name": "Hanna",
            "last_name": "Jones",
        }

        url = detail_url(crew.id)
        response = self.client.put(url, payload, format="multipart")
        crew.refresh_from_db()
        response1 = self.client.get(CREW_URL)
        crew_list = Crew.objects.all()
        serializer = CrewSerializer(crew_list, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data[0], serializer.data[0])
        self.assertEqual(
            crew_list[0].full_name, f"{payload['first_name']} {payload['last_name']}"
        )
