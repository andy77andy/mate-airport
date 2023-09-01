import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.text import slugify


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    if isinstance(instance, Crew):
        filename = f"{slugify(instance.last_name)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/crew/", filename)
    if isinstance(instance, Airplane):
        filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/airplanes/", filename)
    if isinstance(instance, Airport):
        filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/airports/", filename)


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    close_big_city = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self):
        return f"{self.name}, {self.close_big_city}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        verbose_name_plural = "crew"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )

    class Meta:
        ordering = ["source", "destination"]


class Flight(models.Model):
    number = models.CharField(max_length=10, default="12-A-3D")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return f"{self.number}, {self.route}, str({self.departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    row = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_seat_and_row(
        seat: int, seats_in_row: int, row: int, rows: int, error_to_raise
    ):
        if not (1 <= seat <= seats_in_row):
            raise error_to_raise(
                {"seat": f"seat must be in the range [1, {seats_in_row}]"}
            )
        if not (1 <= row <= rows):
            raise error_to_raise({"seat": f"row must be in the range [1, {rows}]"})

    def clean(self):
        Ticket.validate_seat_and_row(
            self.row,
            self.seat,
            self.flight.airplane.seats_in_row,
            self.flight.airplane.rows,
            ValidationError,
        )

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
