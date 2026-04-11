import logging
import sys

from django.shortcuts import render
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets

# from .filters import (
#     EventsFilter
# )

from .models import (
    Events,
    # EventsOfDay,
    EventsOfPoints,
) 

from .serialises import (
    EventsSerializer,
    # EventsOfDaySerializer,
    EventsOfPointsSerializer,
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

class EventsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get',]
    queryset = Events.objects.filter(used=False)
    serializer_class = EventsSerializer

# class EventsOfDayViewSet(
#     viewsets.GenericViewSet,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
# ):
#     permission_classes = [permissions.IsAuthenticated, ]
#     http_method_names = ['get', 'post']
#     queryset = EventsOfDay.objects.all()
#     serializer_class = EventsOfDaySerializer


class EventsOfPointsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get', 'post']
    queryset = EventsOfPoints.objects.all()
    serializer_class = EventsOfPointsSerializer
