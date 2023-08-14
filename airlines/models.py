import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.text import slugify


# def image_file_path(instance, filename):
#     _, extension = os.path.splitext(filename)
#     filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
#
#     return os.path.join("uploads/crew/", filename)

class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    close_big_city = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    # image = models.ImageField(null=True, upload_to=image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        verbose_name_plural = "crew"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"





class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="source_airports")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destination_airports")
    # distance = models.IntegerField()
    # image = models.ImageField(null=True, upload_to=image_file_path

    class Meta:
        ordering = ["source", "destination"]

    def __str__(self):
        return f"{self.source} - {self.destination}"

    # @property
    # def flying_time(self):
    #     return f""


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return f"{self.route}, str({self.departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]

class Ticket(models.Model):
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    # @staticmethod
    # def validate_ticket(row, seat, airplane, error_to_raise):
    #     for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
    #         (row, "row", "rows"),
    #         (seat, "seat", "seats_in_row"),
    #     ]:
    #         count_attrs = getattr(airplane, airplane_attr_name)
    #         if not (1 <= ticket_attr_value <= count_attrs):
    #             raise error_to_raise(
    #                 {
    #                     ticket_attr_name: f"{ticket_attr_name} "
    #                     f"number must be in available range: "
    #                     f"(1, {airplane_attr_name}): "
    #                     f"(1, {count_attrs})"
    #                 }
    #             )
    #
    # def clean(self):
    #     Ticket.validate_ticket(
    #         self.row,
    #         self.seat,
    #         self.flight.airplane,
    #         ValidationError,
    #     )
    #
    # def save(
    #     self,
    #     force_insert=False,
    #     force_update=False,
    #     using=None,
    #     update_fields=None,
    # ):
    #     self.full_clean()
    #     return super(Ticket, self).save(
    #         force_insert, force_update, using, update_fields
    #     )

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]

# Create your models here.
