# from django.shortcuts import render
from datetime import datetime
# from django.db.models import F, Count
# from drf_spectacular.types import OpenApiTypes
# from drf_spectacular.utils import extend_schema, OpenApiParameter
# from rest_framework import viewsets, mixins, status
# from rest_framework.decorators import action
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.response import Response
# from rest_framework.viewsets import GenericViewSet
#
# from cinema.models import Genre, Actor, CinemaHall, Movie, MovieSession, Order
# from cinema.permissions import IsAdminOrIfAuthenticatedReadOnly
#
# from cinema.serializers import (
#     GenreSerializer,
#     ActorSerializer,
#     CinemaHallSerializer,
#     MovieSerializer,
#     MovieSessionSerializer,
#     MovieSessionListSerializer,
#     MovieDetailSerializer,
#     MovieSessionDetailSerializer,
#     MovieListSerializer,
#     OrderSerializer,
#     OrderListSerializer,
#     MovieImageSerializer,
# )
#
#
# class AirplaneTypeViewSet(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     GenericViewSet,
# ):
#     queryset = AirplaneType.objects.all()
#     serializer_class = AirplaneTypeSerializer
#     permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
#
#
# class AirportViewSet(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     GenericViewSet,
# ):
#     queryset = Airport.objects.all()
#     serializer_class = AirportSerializer
#     permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
#

from django.db.models import F, Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from airlines.models import Airplane, Crew, Flight, Route, Order, AirplaneType, Airport
from airlines.permissions import IsAdminOrIfAuthenticatedReadOnly, IsAdminOrReadOnly
from airlines.serializers import AirplaneSerializer, CrewSerializer, RouteSerializer, OrderSerializer, \
    FlightDetailSerializer, FlightListSerializer, AirplaneTypeSerializer, FlightSerializer, OrderListSerializer, \
    AirportSerializer, AirportDetailSerializer


class AirplanePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page-size"
    max_page_size = 100
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    pagination_class = AirplanePagination
    permission_classes = (IsAdminOrReadOnly,)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        """Retrieve the airports with filters"""
        close_big_city = self.request.query_params.get("close_big_city")

        if close_big_city:
            queryset = queryset.filter(close_big_city__icontains=close_big_city)
        return queryset


    def get_serializer_class(self):

        if self.action == "retrieve":
            return AirportDetailSerializer


        # if self.action == "upload_image":
        #     return MovieImageSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="close_big_city",
                type=OpenApiTypes.STR,
                description="Filter by close_big_city (ex. ?close_big_city=Glasgow)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)


class AirplaneTypeViewSet(
    viewsets.ModelViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CrewViewSet(
    viewsets.ModelViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page-size"
    max_page_size = 100


class FlightViewSet(
    viewsets.ModelViewSet,
):
    queryset = Flight.objects.select_related("route", "airplane").annotate(
        tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
        )
    )

    # pagination_class = FlightPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]


    def get_queryset(self):
        """Retrieve the flights with filters"""
        route = self.request.query_params.get("route")
        date = self.request.query_params.get("date")
        arrival_date = self.request.query_params.get("arrival_date")

        queryset = self.queryset
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if arrival_date:
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__arrival_date=arrival_date)

        if route:
            queryset = queryset.filter(
             Q(route__source__close_big_city__icontains=route) |
             Q(route__destination__close_big_city__icontains=route)
    )

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description="Filter by departure_time (ex. ?date=2020-10-10)",
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description="Filter by arrival_time (ex. ?date=2020-10-10)",
            ),
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter by route(ex. ?route=Nice)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)


    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer


        # if self.action == "upload_image":
        #     return MovieImageSerializer
        return FlightSerializer


# #
#
# def get_serializer_class(self):
#     if self.action == "list":
#         return MovieListSerializer
#
#     if self.action == "retrieve":
#         return MovieDetailSerializer
#
#     if self.action == "upload_image":
#         return MovieImageSerializer
#
#     return MovieSerializer

#
class RoutePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page-size"
    max_page_size = 100


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    # pagination_class = RoutePagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            queryset = queryset.filter(source__close_big_city__icontains=source)

        if destination:
            queryset = queryset.filter(source__close_big_city__icontains=destination)

        return queryset
#

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source close big city (ex. ?source=Nice",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination close big city (ex. ?destination=Nice)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)
#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 "source",
#                 type=OpenApiTypes.DATE,
#                 description=(
#                         "Filter by source of Route"
#                         "(ex. ?source=Madrid)"
#                 ),
#             ),
#             OpenApiParameter(
#                 "destination",
#                 type=OpenApiTypes.DATE,
#                 description=(
#                         "Filter by destination of Route"
#                         "(ex. ?route=Madrid)"
#                 ),
#             ),
#         ]
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#
class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page-size"
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    # prefetch_related(
    #     "tickets__movie_session__movie", "tickets__movie_session__cinema_hall"
    # ))
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    """The function limits the ability of the user to view other user's orders"""
    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__flight__airplane")

        return queryset
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return OrderListSerializer
#
#         return OrderSerializer
    """The function automatically create an order exclusively for current user"""
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

# class MovieViewSet(
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     mixins.RetrieveModelMixin,
#     viewsets.GenericViewSet,
# ):
#     queryset = Movie.objects.prefetch_related("genres", "actors")
#     serializer_class = MovieSerializer
#     permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
#
#     @staticmethod
#     def _params_to_ints(qs):
#         """Converts a list of string IDs to a list of integers"""
#         return [int(str_id) for str_id in qs.split(",")]
#
#     def get_queryset(self):
#         """Retrieve the movies with filters"""
#         title = self.request.query_params.get("title")
#         genres = self.request.query_params.get("genres")
#         actors = self.request.query_params.get("actors")
#
#         queryset = self.queryset
#
#         if title:
#             queryset = queryset.filter(title__icontains=title)
#
#         if genres:
#             genres_ids = self._params_to_ints(genres)
#             queryset = queryset.filter(genres__id__in=genres_ids)
#
#         if actors:
#             actors_ids = self._params_to_ints(actors)
#             queryset = queryset.filter(actors__id__in=actors_ids)
#
#         return queryset.distinct()
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return MovieListSerializer
#
#         if self.action == "retrieve":
#             return MovieDetailSerializer
#
#         if self.action == "upload_image":
#             return MovieImageSerializer
#
#         return MovieSerializer
#
#     @action(
#         methods=["POST"],
#         detail=True,
#         url_path="upload-image",
#         permission_classes=[IsAdminUser],
#     )
#     def upload_image(self, request, pk=None):
#         """Endpoint for uploading image to specific movie"""
#         movie = self.get_object()
#         serializer = self.get_serializer(movie, data=request.data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 "genres",
#                 type={"type": "list", "items": {"type": "number"}},
#                 description="Filter by genre id (ex. ?genres=2,5)",
#             ),
#             OpenApiParameter(
#                 "actors",
#                 type={"type": "list", "items": {"type": "number"}},
#                 description="Filter by actor id (ex. ?actors=2,5)",
#             ),
#             OpenApiParameter(
#                 "title",
#                 type=OpenApiTypes.STR,
#                 description="Filter by movie title (ex. ?title=fiction)",
#             ),
#         ]
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)


# def get_queryset(self):
#     date = self.request.query_params.get("date")
#     movie_id_str = self.request.query_params.get("movie")
#
#     queryset = self.queryset
#
#     if date:
#         date = datetime.strptime(date, "%Y-%m-%d").date()
#         queryset = queryset.filter(show_time__date=date)
#
#     if movie_id_str:
#         queryset = queryset.filter(movie_id=int(movie_id_str))
#
#     return queryset

# class ActorViewSet(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     GenericViewSet,
# ):
#     queryset = Actor.objects.all()
#     serializer_class = ActorSerializer
#     permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


# class CinemaHallViewSet(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     GenericViewSet,
# ):
#     queryset = CinemaHall.objects.all()
#     serializer_class = CinemaHallSerializer
#     permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
