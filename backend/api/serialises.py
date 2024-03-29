from datetime import datetime

from rest_framework import serializers

from points.models import Points, Repairs, Services, ServiceMan

new_format = '%Y-%m-%dT%H:%M:%S.%fZ'
old_format = '%d.%m.%Y %H:%M:%S'


class RepairsSerializer(serializers.ModelSerializer):
    point = serializers.CharField(source='point.name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            'view' in self.context
            and self.context['view'].action == 'list'
        ):
            self.fields.update(
                {
                    "tax": serializers.IntegerField(source='point.tax')
                })

    class Meta:
        model = Repairs
        fields = [
            'date', 'point', 'serviceman',
            'category', 'repair', 'comments'
        ]

    def get_date(self, obj, *args, **kwargs):
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, new_format).strftime(old_format)
        return obj.date.strftime(old_format)

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')
        point_name = self.validated_data.pop('point')
        date_query = self.initial_data.get('date')

        try:
            point = Points.objects.get(name=point_name['name'], activ=True)
            print('Поиск точки', point_name['name'])
        except Points.DoesNotExist:
            raise serializers.ValidationError(
                {'point_not_exist': 'Обновите список точек.'}
            )
        try:
            service_man = ServiceMan.objects.get(
                telegram_id=service_man_telegram_id['name']
            )
        except ServiceMan.DoesNotExist:
            raise serializers.ValidationError(
                {'serviceman': 'Инженер не зарегистрирован.'}
            )
        if not service_man.activ:
            raise serializers.ValidationError(
                {'serviceman': 'Инженер уволен.'}
            )
        date = datetime.strptime(date_query, old_format)
        # if Repairs.objects.filter(
        #     date__year=date.year,
        #     date__month=date.month,
        #     date__day=date.day,
        #     point=point
        # ).exists():
        #     raise serializers.ValidationError(
        #         {
        #             'repair_exist': 'Информация по ремонту точки '
        #                             'сегодня уже была добавлена.'
        #         }
        #     )
        date = date.strftime(new_format)

        return Repairs.objects.create(
            **self.validated_data,
            point=point,
            service_man=service_man,
            date=date
        )


class ServicesSerializer(serializers.ModelSerializer):
    point = serializers.CharField(source='point.name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()
    syrupcaramel = serializers.CharField(source='syrup_caramel')
    syrupnut = serializers.CharField(source='syrup_nut')
    syrupother = serializers.CharField(source='syrup_other')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            'view' in self.context
            and self.context['view'].action == 'list'
        ):
            self.fields.update(
                {
                    "tax": serializers.IntegerField(source='point.tax')
                })

    class Meta:
        model = Services
        fields = [
            'date', 'point', 'serviceman', 'collection', 'coffee', 'cream',
            'chocolate', 'raf', 'sugar', 'syrupcaramel', 'syrupnut',
            'syrupother', 'glasses', 'covers', 'stirrer', 'straws'
        ]

    def get_date(self, obj, *args, **kwargs):
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, new_format).strftime(old_format)
        return obj.date.strftime(old_format)

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')
        point_name = self.validated_data.pop('point')
        date_query = self.initial_data.get('date')

        try:
            point = Points.objects.get(name=point_name['name'], activ=True)
            print('Поиск точки', point_name['name'])
        except Points.DoesNotExist:
            raise serializers.ValidationError(
                {'point_not_exist': 'Обновите список точек.'}
            )
        try:
            service_man = ServiceMan.objects.get(
                telegram_id=service_man_telegram_id['name']
            )
        except ServiceMan.DoesNotExist:
            raise serializers.ValidationError(
                {'serviceman': 'Инженер не зарегистрирован.'}
            )
        if not service_man.activ:
            raise serializers.ValidationError(
                {'serviceman': 'Инженер уволен.'}
            )
        date = datetime.strptime(date_query, old_format)
        # if Services.objects.filter(
        #     date__year=date.year,
        #     date__month=date.month,
        #     date__day=date.day,
        #     point=point
        # ).exists():
        #     raise serializers.ValidationError(
        #         {
        #             'service_exist': 'Информация по обслуживанию точки '
        #                              'сегодня уже была добавлена.'
        #         }
        #     )
        date = date.strftime(new_format)

        return Services.objects.create(
            **self.validated_data,
            point=point,
            service_man=service_man,
            date=date
        )


class ServiceManSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMan
        fields = ['id', 'name', 'telegram_id', 'activ',]
