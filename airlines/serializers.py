from django.db import transaction
from rest_framework import serializers

from airlines.models import Airplane, Crew, Flight, Route, Order, Ticket, AirplaneType


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type",)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name",)


class FlightListSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField()
    class Meta:
        model = Flight
        fields = ("id", "number", "route", "airplane", "departure_time", "arrival_time", "tickets_available")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "number", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        source="airplane",
        many=False,
        read_only=True,
        slug_field="airplane_type"
    )

    class Meta:
        model = Flight
        fields = ("id", "number", "route", "airplane", "departure_time", "arrival_time", "airplane_type")

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination",)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "flight", "row", "seat",)

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat_and_row(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError
        )
        return data

class TicketDetailSerializer(serializers.ModelSerializer):
    flight = FlightDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "source", "destination", "route")




class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", )


    '''redefine method create to allow create tivkets while creating order'''
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
        fields = ("id", "tickets", "created_at", )

