from django_filters.rest_framework import (
    FilterSet,
)
from django_filters.widgets import RangeWidget

from .models import Events

class EventsFilter(FilterSet):
    class Meta:
        model = Events
        fields = ['used', ]
