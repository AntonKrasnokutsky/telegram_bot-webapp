from django_filters.rest_framework import (
    DateFromToRangeFilter,
    FilterSet
)

from points.models import Repairs, Services


class ServicesFilter(FilterSet):
    date = DateFromToRangeFilter()

    class Meta:
        model = Services
        fields = ['date', 'service_man', 'point',]


class RepairsFilter(FilterSet):
    date = DateFromToRangeFilter()

    class Meta:
        model = Repairs
        fields = ['date', 'service_man', 'point',]
