from django.contrib import admin

from airlines.models import Route, Flight, Airport, Airplane, AirplaneType, Order, Ticket, Crew


# Register your models here.
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    pass


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    pass


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    pass


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    pass


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    pass


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    pass
