from django_filters.rest_framework import (
    DateFromToRangeFilter,
    FilterSet
)

from points.models import Services


class ServicesFilter(FilterSet):
    date = DateFromToRangeFilter()

    class Meta:
        model = Services
        fields = ['date',]
