from datetime import datetime

from django.db.models import F, Count
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from airlines.models import Airport, Route, Flight, Airplane, AirplaneType
from airlines.serializers import FlightListSerializer

FLIGHT_URL = reverse("airlines:flight-list")


def sample_airport(**params):
    defaults = {
        "name": "Test",
        "close_big_city": "Test city",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    defaults = {
        "name": "Test",
        "rows": 3,
        "seats_in_row": 10,
        "airplane_type": sample_airplane_type(),
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class AuthenticatedFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test1.com", "test1234")
        self.client.force_authenticate(self.user)

    def test_list_flight(self):
        airport1 = sample_airport(
            name="test1",
            close_big_city="Rome",
        )
        airport2 = sample_airport(
            name="test2",
            close_big_city="Lviv",
        )
        airport3 = sample_airport(
            name="test3",
            close_big_city="Riga",
        )
        airport4 = sample_airport(
            name="test4",
            close_big_city="Oslo",
        )
        route1 = Route.objects.create(source=airport1, destination=airport2)
        route2 = Route.objects.create(source=airport3, destination=airport4)
        airplane1 = sample_airplane()
        airplane2 = sample_airplane()

        flight1 = Flight.objects.create(
            number="Test",
            route=route1,
            airplane=airplane1,
            departure_time="2020-10-08 18:00:00",
            arrival_time="2020-10-08 18:00:00",
        )

        flight2 = Flight.objects.create(
            number="Test",
            route=route2,
            airplane=airplane2,
            departure_time=datetime(2023, 8, 21, 10, 30),
            arrival_time=datetime(2023, 8, 22, 10, 30),
        )
        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
        """Create response from flight-list"""
        response = self.client.get(FLIGHT_URL)
        """Create response from flight-list with filtering"""
        response1 = self.client.get(FLIGHT_URL, {"route": "Riga"})
        response2 = self.client.get(FLIGHT_URL, {"date": "2023-08-21"})

        serializer = FlightListSerializer(flights, many=True)
        serializer1 = FlightListSerializer(
            flights[1],
        )
        serializer2 = FlightListSerializer(
            flights[1],
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn(serializer1.data, response1.data)
        self.assertIn(serializer2.data, response2.data)
