from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airlines.models import Airport, Route
from airlines.serializers import RouteSerializer

ROUTE_URL = reverse("airlines:route-list")


def sample_airport(**params):
    defaults = {
        "name": "Test",
        "close_big_city": "Test city",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test1.com", "test1234")
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        airport1 = sample_airport(
            name="test1",
            close_big_city="Test city1",
        )
        airport2 = sample_airport(
            name="test2",
            close_big_city="Test city2",
        )
        Route.objects.create(source=airport1, destination=airport2)

        response = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
