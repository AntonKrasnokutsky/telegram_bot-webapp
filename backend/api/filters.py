from django_filters.rest_framework import (
    DateFromToRangeFilter,
    FilterSet
)
from django_filters.widgets import RangeWidget

from points.models import Audit, Repairs, Services


class DurationRangeWidget(RangeWidget):
    suffixes = ['after', 'before']


class ServicesFilter(FilterSet):
    date = DateFromToRangeFilter(
        widget=DurationRangeWidget(attrs={'type': 'date'})
    )

    class Meta:
        model = Services
        fields = ['date', 'service_man', 'point',]


class RepairsFilter(FilterSet):
    date = DateFromToRangeFilter(
        widget=DurationRangeWidget(attrs={'type': 'date'})
    )

    class Meta:
        model = Repairs
        fields = ['date', 'service_man', 'point',]


class AuditFilter(FilterSet):

    class Meta:
        model = Audit
        fields = ['date', 'service_man', ]
