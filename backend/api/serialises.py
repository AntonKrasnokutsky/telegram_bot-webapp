from datetime import datetime

from rest_framework import serializers

from points.models import (
    Audit,
    ExternalCompanies,
    ExternalRepairs,
    ExternalTypeWorkRepairs,
    ExtermalWorkInRepairs,
    FuelCompensation,
    Points,
    Repairs,
    ServiceMan,
    Services,
    TypeWorkRepairs
)

new_format = '%Y-%m-%dT%H:%M:%S.%fZ'
old_format = '%d.%m.%Y %H:%M:%S'


class TypeWorkRepairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeWorkRepairs
        fields = ['typework', 'price', ]


class FuelCompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelCompensation
        fields = ['distance', 'price', ]


class RepairsSerializer(serializers.ModelSerializer):
    point = serializers.CharField(source='point.name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context:
            if self.context['view'].action == 'list':
                self.fields.update(
                    {
                        "typework": TypeWorkRepairsSerializer(
                            many=True,
                            required=False
                        ),
                        "fuelcompensation": FuelCompensationSerializer(
                            required=False
                        ),
                    })
            if self.context['view'].action == 'create':
                self.fields.update(
                    {
                        "typework": serializers.ListField(required=False),
                        "fuelcompensation": serializers.CharField(
                            required=False
                        ),
                    })

    class Meta:
        model = Repairs
        fields = ['date', 'point', 'serviceman', 'comments',]

    def get_date(self, obj, *args, **kwargs):
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, new_format).strftime(old_format)
        return obj.date.strftime(old_format)

    def __get_works(self, *args, **kwargs):
        try:
            typework = self.validated_data.pop('typework')
        except KeyError:
            return None
        type_works = []
        for work in typework:
            try:
                type_works.append(TypeWorkRepairs.objects.get(
                    typework=work,
                    activ=True,
                ))
            except TypeWorkRepairs.DoesNotExist:
                raise serializers.ValidationError(
                    {'type_works': f'Тип работ не добавлен: {work}'}
                )
        return type_works

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')
        point_name = self.validated_data.pop('point')
        date_query = self.initial_data.get('date')
        try:
            fuel_compensation = self.validated_data.pop('fuelcompensation')
            fuelcompensation = FuelCompensation.objects.get(
                distance=fuel_compensation
            )
        except KeyError:
            fuelcompensation = None
        except FuelCompensation.DoesNotExist:
            fuelcompensation = None

        try:
            point = Points.objects.get(name=point_name['name'], activ=True)
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
        date = date.strftime(new_format)
        typework = self.__get_works()
        repairs = Repairs.objects.create(
            **self.validated_data,
            point=point,
            service_man=service_man,
            date=date,
            fuelcompensation=fuelcompensation,
        )
        if typework:
            repairs.typework.set(typework)
        self.fields.update(
            {
                "tax": serializers.IntegerField(source='point.tax'),
                "typework": TypeWorkRepairsSerializer(
                    many=True,
                    required=False
                ),
                "fuelcompensation": FuelCompensationSerializer(required=False),
            })
        return repairs


class ServicesSerializer(serializers.ModelSerializer):
    point = serializers.CharField(source='point.name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()
    syrupcaramel = serializers.CharField(source='syrup_caramel')
    syrupnut = serializers.CharField(source='syrup_nut')
    syrupother = serializers.CharField(source='syrup_other')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context:
            if self.context['view'].action == 'list':
                self.fields.update(
                    {
                        "tax": serializers.IntegerField(source='point.tax'),
                        "fuelcompensation": FuelCompensationSerializer(
                            required=False
                        ),
                    })
            if self.context['view'].action == 'create':
                self.fields.update(
                    {
                        "fuelcompensation": serializers.CharField(
                            required=False
                        ),
                    })

    class Meta:
        model = Services
        fields = [
            'date', 'point', 'serviceman', 'collection', 'coffee', 'mokko',
            'cream', 'chocolate', 'raf', 'sugar', 'syrupcaramel', 'syrupnut',
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
            fuel_compensation = self.validated_data.pop('fuelcompensation')
            fuelcompensation = FuelCompensation.objects.get(
                distance=fuel_compensation
            )
        except KeyError:
            fuelcompensation = None
        except FuelCompensation.DoesNotExist:
            fuelcompensation = None

        try:
            point = Points.objects.get(name=point_name['name'], activ=True)
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
        date = date.strftime(new_format)

        return Services.objects.create(
            **self.validated_data,
            point=point,
            service_man=service_man,
            date=date,
            fuelcompensation=fuelcompensation,
        )


class ServiceManSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMan
        fields = ['id', 'name', 'telegram_id', 'activ', 'office_engineer']


class AuditSerializer(serializers.ModelSerializer):
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.DateField(
        format="%d.%m.%Y",
        input_formats=['%d.%m.%Y']
    )
    syrup_caramel = serializers.CharField()
    syrup_nut = serializers.CharField()

    class Meta:
        model = Audit
        fields = [
            'date', 'serviceman', 'coffee', 'mokko', 'cream', 'chocolate',
            'raf', 'sugar', 'glasses', 'covers', 'straws', 'stirrer',
            'syrup_caramel', 'syrup_nut',
        ]

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')

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

        return Audit.objects.create(
            **self.validated_data,
            service_man=service_man,
        )


# Ремонт оборудования сторонних компаний
class ExternalTypeWorkRepairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalTypeWorkRepairs
        fields = ['typework', 'price', ]


class ExtermalWorkInRepairsSerializer(serializers.ModelSerializer):
    external_work = TypeWorkRepairsSerializer()

    class Meta:
        model = ExtermalWorkInRepairs
        fields = ['external_work', 'count', ]


class ExternalRepairsSerializer(serializers.ModelSerializer):
    company = serializers.CharField(source='company.company_name')
    serviceman = serializers.CharField(source='service_man.name')
    date = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context:
            if self.context['view'].action == 'list':
                self.fields.update(
                    {
                        "types_work": ExtermalWorkInRepairsSerializer(
                            many=True,
                        ),

                    })
            if self.context['view'].action == 'create':
                self.fields.update(
                    {
                        "types_work": serializers.ListField(),
                    })

    class Meta:
        model = ExternalRepairs
        fields = [
            'date',
            'company',
            'serviceman',
            'serial_num_coffe',
            'comments',
        ]

    def get_date(self, obj, *args, **kwargs):
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, new_format).strftime(old_format)
        return obj.date.strftime(old_format)

    def __get_external_works(self, *args, **kwargs):
        try:
            typeworks = self.validated_data.pop('types_work')
        except KeyError:
            return None
        type_works = []

        for typework in typeworks:
            try:
                work = ExternalTypeWorkRepairs.objects.get(
                    typework=typework['external_work'],
                    activ=True,
                )
                type_works.append(
                    {
                        'typework': work,
                        'count': typework['count'],
                    }
                )
            except ExternalTypeWorkRepairs.DoesNotExist:
                raise serializers.ValidationError(
                    {'external_type_works': 'Тип работ не добавлен: '
                                            f'{typework["external_work"]}'}
                )
        return type_works

    def __add_type_works(self, repairs, typeworks, *args, **kwargs):
        for typework in typeworks:
            work_in_repair = ExtermalWorkInRepairs()
            work_in_repair.external_repair = repairs
            work_in_repair.external_work = typework['typework']
            work_in_repair.count = typework['count']
            work_in_repair.save()

    def create(self, *args, **kwargs):
        service_man_telegram_id = self.validated_data.pop('service_man')
        company_name = self.validated_data.pop('company')
        date_query = self.initial_data.get('date')
        try:
            company = ExternalCompanies.objects.get(
                company_name=company_name['company_name'],
                activ=True
            )
        except ExternalCompanies.DoesNotExist:
            raise serializers.ValidationError(
                {'company_not_exist': 'Такой компании нет.'}
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
        if not service_man.office_engineer:
            raise serializers.ValidationError(
                {
                    'serviceman': 'Доступ не предоставлен. '
                    'Обратитесь к администратору'
                }
            )
        date = datetime.strptime(date_query, old_format)
        date = date.strftime(new_format)
        typeworks = self.__get_external_works()
        repairs = ExternalRepairs.objects.create(
            **self.validated_data,
            company=company,
            service_man=service_man,
            date=date,
        )
        if typeworks:
            self.__add_type_works(repairs, typeworks)
        self.fields.update(
            {
                "types_work": ExtermalWorkInRepairsSerializer(
                    many=True,
                    required=True,
                ),

            })

        return repairs
