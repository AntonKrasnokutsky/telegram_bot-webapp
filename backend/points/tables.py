import django_tables2 as tables

from .models import (
    Audit,
    ExternalRepairs,
    Repairs,
    Services,
)


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
            'glasses',
            'covers',
            'straws',
            'stirrer',
            'syrup_caramel',
            'syrup_nut',
            'mokko',
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
            'mokko',
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


# Ремонт оборудования сторонних компаний
class ExternalRepairsTable(tables.Table):
    types_work = tables.Column()

    export_formats = ['xls', 'xlsx']

    class Meta:
        model = ExternalRepairs
        per_page = 20
        fields = (
            'date',
            'service_man',
            'company',
            'types_work',
            'serial_num_coffe',
        )

    def render_types_work(self, value):
        result = ''
        for work in value.all():
            result += str(work.external_work)
            result += f' Количество: {work.count}\n'
        return result
