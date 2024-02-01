from datetime import datetime

from rest_framework import serializers

from points.models import Points, Services, ServiceMan

from .exceptions import ServiceInfoExistError, ServiceManUnregisteredError


class ServicesSerializer(serializers.ModelSerializer):
    point = serializers.CharField(source='point.name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()
    syrupcaramel = serializers.CharField(source='syrup_caramel')
    syrupnut = serializers.CharField(source='syrup_nut')
    syrupother = serializers.CharField(source='syrup_other')

    class Meta:
        model = Services
        fields = [
            'date', 'point', 'serviceman', 'collection', 'coffee', 'cream',
            'chocolate', 'raf', 'sugar', 'syrupcaramel', 'syrupnut',
            'syrupother', 'glasses', 'covers', 'stirrer', 'straws'
        ]

    def get_date(self, obj, *args, **kwargs):
        new_format = '%d.%m.%Y %H:%M:%S'
        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, old_format).strftime(new_format)
        return obj.date.strftime(new_format)

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')
        point_name = self.validated_data.pop('point')
        date_query = self.initial_data.get('date')
        new_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        old_format = '%d.%m.%Y %H:%M:%S'

        point = Points.objects.get(name=point_name['name'])
        try:
            service_man = ServiceMan.objects.get(
                telegram_id=service_man_telegram_id['name']
            )
        except ServiceMan.DoesNotExist:
            raise ServiceManUnregisteredError(
                {'serviceman': 'Инженер не зарегистрирован.'}
            )
        date = datetime.strptime(date_query, old_format)
        if Services.objects.filter(
            date__year=date.year,
            date__month=date.month,
            date__day=date.day,
            point=point
        ).exists():
            raise ServiceInfoExistError(
                {
                    'service_exist': 'Информация по обслуживанию точки '
                                     'сегодня уже была добавлена.'
                }
            )
        date = date.strftime(new_format)

        return Services.objects.create(
            **self.validated_data,
            point=point,
            service_man=service_man,
            date=date
        )
