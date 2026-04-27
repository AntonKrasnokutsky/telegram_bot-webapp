import django_tables2 as tables

from .models import (
    Audit,
    ExternalRepairs,
    ExtermalWorkInRepairs,
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
    types_work = tables.Column(verbose_name='Виды работ')

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
            'comments',
        )

    def render_types_work(self, record):
        # Получаем все связанные работы для текущего ремонта
        works = ExtermalWorkInRepairs.objects.filter(external_repair=record)
        if not works.exists():
            return 'Нет работ'

        result_lines = []
        for work in works:
            # Форматируем каждую работу: вид + тариф + количество
            work_info = f'{work.external_work.typework}'
            work_info += f' (Тариф: {work.external_work.price} руб.)'
            work_info += f' — Кол-во: {work.count}'
            result_lines.append(work_info)
        # Объединяем строки с переносом
        return '\n'.join(result_lines)


class ExternalRepairsManTable(tables.Table):
    types_work = tables.Column(verbose_name='Виды работ')

    class Meta:
        model = ExternalRepairs
        per_page = 20
        fields = (
            'date',
            'service_man',
            'company',
            'types_work',
            'serial_num_coffe',
            'comments',
        )

    def render_types_work(self, record):
        # Получаем все связанные работы для текущего ремонта
        works = ExtermalWorkInRepairs.objects.filter(external_repair=record)
        if not works.exists():
            return 'Нет работ'

        result_lines = []
        for work in works:
            # Форматируем каждую работу: вид + тариф + количество
            work_info = f'{work.external_work.typework}'
            work_info += f' (Тариф: {work.external_work.price} руб.)'
            work_info += f' — Кол-во: {work.count}'
            result_lines.append(work_info)
        # Объединяем строки с переносом
        return '\n'.join(result_lines)
