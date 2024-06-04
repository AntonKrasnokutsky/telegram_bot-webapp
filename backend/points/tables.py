import django_tables2 as tables

from .models import Repairs, Services


class RepairsTable(tables.Table):
    export_formats = ['xls', 'xlsx']

    class Meta:
        model = Repairs
        # unlocalize = ('date', )
        per_page = 20
        fields = (
            'date',
            'service_man',
            'point',
            'typework',
            'fuelcompensation',
            'comments',
        )


class ServiceTable(tables.Table):
    export_formats = ['xls', 'xlsx']

    class Meta:
        model = Services
        # unlocalize = ('date', )
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
