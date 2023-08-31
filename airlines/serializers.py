from django.db import transaction
from rest_framework import serializers

from airlines.models import (
    Airplane,
    Crew,
    Flight,
    Route,
    Order,
    Ticket,
    AirplaneType,
    Airport,
)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "image")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "close_big_city",
        )


class AirportDetailSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    transfer = serializers.BooleanField(default=True)
    destinations = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "close_big_city",
            "image",
            "transfer",
            "destinations",
        )

    def get_destinations(self, obj):
        source_routes = Route.objects.filter(source=obj)
        destination_airport_names = [route.destination.name for route in source_routes]
        return destination_airport_names


class CloseBigCityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "image")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "image")


class RouteSerializer(serializers.ModelSerializer):
    # source = serializers.StringRelatedField(many=False)
    # destination = serializers.StringRelatedField(many=False)

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteAirportSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField(many=False)
    destination = serializers.StringRelatedField(many=False)

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class FlightListSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField()
    route = serializers.StringRelatedField(many=False)

    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "number", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False, read_only=True)
    airplane = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    airplane_type = serializers.SlugRelatedField(
        source="airplane.airplane-type", many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "airplane_type",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "flight",
            "row",
            "seat",
        )

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat_and_row(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError,
        )
        return data


class TicketDetailSerializer(serializers.ModelSerializer):
    flight = FlightDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
            "created_at",
        )

    """redefine method create to allow create tickets while creating order"""

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for tickets_data in tickets_data:
                Ticket.objects.create(order=order, **tickets_data)
            return order


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
            "created_at",
        )
