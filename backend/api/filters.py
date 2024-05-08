from django_filters.rest_framework import (
    DateFromToRangeFilter,
    FilterSet
)
from django_filters.widgets import RangeWidget

from points.models import Repairs, Services


class ServicesFilter(FilterSet):
    date = DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))

    class Meta:
        model = Services
        fields = ['date', 'service_man', 'point',]


class RepairsFilter(FilterSet):
    date = DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))

    class Meta:
        model = Repairs
        fields = ['date', 'service_man', 'point',]
