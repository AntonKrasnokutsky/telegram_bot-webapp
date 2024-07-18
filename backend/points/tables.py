import django_tables2 as tables

from .models import Audit, Repairs, Services


class AuditTable(tables.Table):
    export_formats = ['xls', 'xlsx']

    class Meta:
        model = Audit
        per_page = 20
        fields = (
            'date',
            'service_man',
            'coffee',
            'cream',
            'chocolate',
            'raf',
            'sugar',
            'syrup_caramel',
            'syrup_nut',
            'glasses',
            'covers',
            'stirrer',
            'straws',
        )


class RepairsTable(tables.Table):
    export_formats = ['xls', 'xlsx']

    class Meta:
        model = Repairs
        per_page = 20
        fields = (
            'date',
            'service_man',
            'point',
            'typework',
            'fuelcompensation__distance',
            'fuelcompensation__price',
            'comments',
        )


class ServiceTable(tables.Table):
    export_formats = ['xls', 'xlsx']

    class Meta:
        model = Services
        per_page = 20
        fields = (
            'date',
            'service_man',
            'point',
            'point__tax',
            'fuelcompensation',
            'collection',
            'coffee',
            'cream',
            'chocolate',
            'raf',
            'sugar',
            'syrup_caramel',
            'syrup_nut',
            'syrup_other',
            'glasses',
            'covers',
            'stirrer',
            'straws',
        )
