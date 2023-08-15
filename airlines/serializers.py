from django.db import transaction
from rest_framework import serializers

from airlines.models import Airplane, Crew, Flight, Route, Order, Ticket


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type",)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name",)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination",)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination",)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for tickets_data in tickets_data:
                Ticket.objects.create(order=order, **tickets_data)
            return order
