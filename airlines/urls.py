from django.urls import path, include
from rest_framework import routers

from airlines.views import (
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
    RouteViewSet,
    OrderViewSet,
    AirplaneTypeViewSet,
    AirportViewSet,
)

router = routers.DefaultRouter()
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("crew", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airlines"
