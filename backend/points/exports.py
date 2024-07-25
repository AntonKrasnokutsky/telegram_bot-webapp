from django_tables2.export.views import TableExport
from tablib import Dataset

from .models import TypeWorkRepairs


class AuditTableExport(TableExport):
    def table_to_dataset(self, table, exclude_columns, dataset_kwargs=None):
        headers = [
            'Дата',
            'Наименование',
            'Количествоа',
        ]
        headers_position_value = {}
        headers_position_data = {}
        data = ['Дата', 'Исполнитель']

        """Transform a table to a tablib dataset."""

        def default_dataset_title():
            try:
                return table.Meta.model._meta.verbose_name_plural.title()
            except AttributeError:
                return "Export Data"

        kwargs = {"title": default_dataset_title()}
        kwargs.update(dataset_kwargs or {})
        dataset = Dataset(**kwargs)
        for i, row in enumerate(
            table.as_values(exclude_columns=exclude_columns)
        ):
            if i == 0:
                for pos, field in enumerate(row):
                    if field in data:
                        headers_position_data[field] = pos
                    else:
                        headers_position_value[field] = pos
                dataset.headers = headers
            else:
                names_value = list(headers_position_value.keys())
                names_value.sort()
                for name in names_value:
                    rows = [
                        row[headers_position_data['Дата']],
                        f'{row[headers_position_data["Исполнитель"]]} {name}',
                        row[headers_position_value[name]],
                    ]
                    dataset.append(rows)
        return dataset


class RepairsTableExport(TableExport):
    def table_to_dataset(self, table, exclude_columns, dataset_kwargs=None):
        headers = [
            'Дата время',
            'Исполнитель',
            'Точка',
            'Вид работ',
            'Стоимость работ',
            'Компенсация ГСМ',
            'Тариф ГСМ',
            'Комментарий',
        ]
        index = None
        """Transform a table to a tablib dataset."""

        def default_dataset_title():
            try:
                return table.Meta.model._meta.verbose_name_plural.title()
            except AttributeError:
                return "Export Data"

        kwargs = {"title": default_dataset_title()}
        kwargs.update(dataset_kwargs or {})
        dataset = Dataset(**kwargs)
        for i, row in enumerate(
            table.as_values(exclude_columns=exclude_columns)
        ):
            if i == 0:
                index = row.index('Вид работ')
                dataset.headers = headers
            else:
                price = 0
                if row[index]:
                    for work in row[index].split(', '):
                        price += TypeWorkRepairs.objects.get(
                            typework=work.split(' Тариф: ')[0],
                            activ=True
                        ).price
                    row.insert(index + 1, price)
                else:
                    row.insert(index + 1, '')
                dataset.append(row)
        return dataset
