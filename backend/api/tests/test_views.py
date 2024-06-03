import json
import zoneinfo
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from points.models import (
    FuelCompensation,
    Points,
    Repairs,
    Services,
    ServiceMan,
    TypeWorkRepairs
)

User = get_user_model()
client_authenticate = APIClient()
client_not_authenticate = APIClient()


class ServiceManTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            email='a@a.ru',
            username='test_user',
            first_name='test_first_name',
            last_name='test_last_name',
            password='testPassword123',
        )
        client_authenticate.force_authenticate(cls.test_user)
        service_man = ServiceMan.objects.create(
            name='Имя',
            telegram_id=123456,
            activ=True
        )
        cls.service_mans = [{
            'id': service_man.id,
            'name': 'Имя',
            'telegram_id': 123456,
            'activ': True,
        }]
        service_man = ServiceMan.objects.create(
            name='Имя2',
            telegram_id=1234567,
            activ=True
        )
        cls.service_mans.append({
            'id': service_man.id,
            'name': 'Имя2',
            'telegram_id': 1234567,
            'activ': True,
        })

    def test_serviceman_list(self, *args, **kwargs):
        request = client_authenticate.get(
            reverse(
                'api:serviceman-list'
            ))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(ServiceMan.objects.all().count(), len(request.data))

        request = client_not_authenticate.get(
            reverse(
                'api:serviceman-list'
            ))
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serviceman_create(self, *args, **kwargs):
        data_reqest = {
            'name': 'Имя3',
            'telegram_id': 7347563478,
            'activ': True,
        }

        request = client_authenticate.post(
            reverse('api:serviceman-list'),
            data=data_reqest
        )
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in request.data)
        for field, value in data_reqest.items():
            with self.subTest(value=value):
                self.assertEqual(request.data[field], value)

        base_answer = {
            'telegram_id': ['service man с таким telegram id уже существует.']
        }
        request = client_authenticate.post(
            reverse('api:serviceman-list'),
            data=data_reqest
        )
        request_answer = json.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        for field, value in base_answer.items():
            with self.subTest(value=value):
                self.assertEqual(request_answer[field], value)

        request = client_not_authenticate.post(
            reverse('api:serviceman-list'),
            data=data_reqest
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serviceman_change(self, *args, **kwargs):
        serviceman_change = self.service_mans[1].copy()
        request = client_authenticate.post(
            reverse(
                'api:serviceman-change-activ',
                args=[serviceman_change['id']]
            )
        )
        request_answer = json.loads(request.content)
        serviceman_change.pop('id')
        serviceman_change['activ'] = not serviceman_change['activ']
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        for field, value in serviceman_change.items():
            with self.subTest(value=value):
                self.assertEqual(request_answer[field], value)

        request = client_not_authenticate.post(
            reverse(
                'api:serviceman-change-activ',
                args=[self.service_mans[1]['id']]
            )
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serviceman_filter(self, *args, **kwargs):
        serviceman_filtered = self.service_mans[1].copy()
        request = client_authenticate.get(
            reverse(
                'api:serviceman-list'
            ),
            **{
                'QUERY_STRING':
                f'telegram_id={serviceman_filtered["telegram_id"]}'
            }
        )
        request_answer = json.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request_answer), 1)
        for field, value in serviceman_filtered.items():
            with self.subTest(value=value):
                self.assertEqual(request_answer[0][field], value)

        request = client_authenticate.get(
            reverse(
                'api:serviceman-list'
            ),
            **{
                'QUERY_STRING':
                'telegram_id=0'
            }
        )
        request_answer = json.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(request_answer), 0)

        request = client_not_authenticate.get(
            reverse(
                'api:serviceman-list'
            ),
            **{
                'QUERY_STRING':
                f'telegram_id={serviceman_filtered["telegram_id"]}'
            }
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class ServicesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            email='a@a.ru',
            username='test_user_service',
            first_name='test_first_name',
            last_name='test_last_name',
            password='testPassword123',
        )
        client_authenticate.force_authenticate(cls.test_user)
        cls.service_man = ServiceMan.objects.create(
            name='Имя',
            telegram_id=123456,
            activ=True
        )
        cls.point_one = Points.objects.create(
            name='Тестовая точка 1',
            tax=1,
            activ=True
        )
        cls.point_two = Points.objects.create(
            name='Тестоваяточка2',
            tax=2,
            activ=True
        )
        date = datetime.strptime('10.01.2024 12:02:23', '%d.%m.%Y %H:%M:%S')
        service1 = Services.objects.create(
            date=date,
            service_man=cls.service_man,
            point=cls.point_one,
            collection=10,
            coffee=1,
            cream=1,
            chocolate=0,
            raf=0,
            sugar=50,
            syrup_caramel=0,
            syrup_nut=1,
            syrup_other=1,
            glasses=50,
            covers=50,
            stirrer=50,
            straws=0
        )
        cls.services = [
            {
                'date': service1.date.strftime("%d.%m.%Y %H:%M:%S"),
                'serviceman': service1.service_man.name,
                'point': service1.point.name,
                'collection': service1.collection,
                'coffee': service1.coffee,
                'cream': service1.cream,
                'chocolate': service1.chocolate,
                'raf': service1.raf,
                'sugar': service1.sugar,
                'syrupcaramel': service1.syrup_caramel,
                'syrupnut': service1.syrup_nut,
                'syrupother': service1.syrup_other,
                'glasses': service1.glasses,
                'covers': service1.covers,
                'stirrer': service1.stirrer,
                'straws': service1.straws,
                'tax': service1.point.tax
            }
        ]
        cls.fuelcompensation = FuelCompensation.objects.create(
            distance='Расстояние',
            price=500,
            activ=True,
        )
        date = datetime.strptime('15.05.2024 10:44:09', '%d.%m.%Y %H:%M:%S')
        service = Services.objects.create(
            date=date,
            service_man=cls.service_man,
            point=cls.point_two,
            collection=20,
            coffee=0,
            cream=0,
            chocolate=1,
            raf=1,
            sugar=0,
            syrup_caramel=1,
            syrup_nut=0,
            syrup_other=0,
            glasses=100,
            covers=100,
            stirrer=100,
            straws=50,
            fuelcompensation=cls.fuelcompensation,
        )
        cls.services.append(
            {
                'date': service.date.strftime("%d.%m.%Y %H:%M:%S"),
                'serviceman': service.service_man.name,
                'point': service.point.name,
                'collection': service.collection,
                'coffee': service.coffee,
                'cream': service.cream,
                'chocolate': service.chocolate,
                'raf': service.raf,
                'sugar': service.sugar,
                'syrupcaramel': service.syrup_caramel,
                'syrupnut': service.syrup_nut,
                'syrupother': service.syrup_other,
                'glasses': service.glasses,
                'covers': service.covers,
                'stirrer': service.stirrer,
                'straws': service.straws,
                'tax': service.point.tax,
                'fuelcompensation': {
                    'distance': 'Расстояние',
                    'price': 500
                }
            }
        )

    def test_service_create(self, *args, **kwargs):
        zone = zoneinfo.ZoneInfo("Europe/Moscow")
        data = {
            'date': datetime.now(zone).strftime("%d.%m.%Y %H:%M:%S"),
            'serviceman': self.service_man.telegram_id,
            'point': self.point_one.name,
            'collection': 10,
            'coffee': 1,
            'cream': 1,
            'chocolate': 0,
            'raf': 0,
            'sugar': 1,
            'syrupcaramel': 0,
            'syrupnut': 1,
            'syrupother': 1,
            'glasses': 50,
            'covers': 50,
            'stirrer': 50,
            'straws': 0
        }
        request = client_not_authenticate.post(
            reverse(
                'api:services_v2'
            ),
            data)
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        request = client_authenticate.post(
            reverse(
                'api:services_v2'
            ),
            data=data)
        data['serviceman'] = self.service_man.name
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        for field, value in data.items():
            with self.subTest(value=value):
                self.assertEqual(str(request.data[field]), str(value))

        data['serviceman'] = self.service_man.telegram_id,
        data['fuelcompensation'] = self.fuelcompensation.distance
        request = client_authenticate.post(
            reverse(
                'api:services_v2'
            ),
            data=data)
        data['serviceman'] = self.service_man.name
        data['fuelcompensation'] = self.fuelcompensation
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        for field, value in data.items():
            with self.subTest(value=value):
                self.assertEqual(str(request.data[field]), str(value))

    def test_service_list(self, *args, **kwargs):
        request = client_not_authenticate.get(
            reverse(
                'api:services_v2'
            ))
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        request = client_authenticate.get(
            reverse(
                'api:services_v2'
            ))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        request_answer = json.loads(request.content)
        self.assertEqual(Services.objects.all().count(), len(request_answer))

        for service in range(len(self.services)):
            for field, value in self.services[service].items():
                with self.subTest(value=value):
                    self.assertEqual(
                        str(request_answer[service][field]),
                        str(value)
                    )

    def test_services_filtered(self, *args, **kwargs):
        request = client_authenticate.get(
            reverse(
                'api:services_v2'
            ),
            **{
                'QUERY_STRING':
                'date_after=2024-01-11&date_before=2024-05-14',

            }
        )
        self.assertEqual(len(json.loads(request.content)), 0)
        request = client_authenticate.get(
            reverse(
                'api:services_v2'
            ),
            **{
                'QUERY_STRING':
                'date_after=2024-01-10&date_before=2024-05-16',

            }
        )
        self.assertEqual(len(json.loads(request.content)), 2)

        request = client_authenticate.get(
            reverse(
                'api:services_v2'
            ),
            **{
                'QUERY_STRING':
                'date_after=2024-01-11',

            }
        )
        self.assertEqual(len(json.loads(request.content)), 1)

        request = client_authenticate.get(
            reverse(
                'api:services_v2'
            ),
            **{
                'QUERY_STRING':
                'date_before=2024-05-14',

            }
        )
        self.assertEqual(len(json.loads(request.content)), 1)


class RepairsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            email='a@a.ru',
            username='test_user_repairs',
            first_name='test_first_name',
            last_name='test_last_name',
            password='testPassword123',
        )
        client_authenticate.force_authenticate(cls.test_user)
        cls.service_man = ServiceMan.objects.create(
            name='Имя',
            telegram_id=12345,
            activ=True
        )
        cls.point_one = Points.objects.create(
            name='Тестовая точка 1',
            tax=1,
            activ=True
        )
        cls.point_two = Points.objects.create(
            name='Тестоваяточка2',
            tax=2,
            activ=True
        )
        date = datetime.strptime('10.01.2024 12:02:23', '%d.%m.%Y %H:%M:%S')
        cls.type_work = TypeWorkRepairs.objects.create(
            typework='Работа ремонта',
            price=10,
            activ=True
        )
        cls.fuelcompensation = FuelCompensation.objects.create(
            distance='Расстояние',
            price=500,
            activ=True,
        )
        repair = Repairs.objects.create(
            date=date,
            service_man=cls.service_man,
            point=cls.point_one,
            # typework=cls.type_work,
            fuelcompensation=cls.fuelcompensation,
            comments='Коментарий'
        )
        repair.typework.add(cls.type_work)
        cls.repairs = [{
            'date': repair.date.strftime("%d.%m.%Y %H:%M:%S"),
            'serviceman': repair.service_man.name,
            'point': repair.point.name,
            'typework': [rep.typework for rep in repair.typework.all()],
            'fuelcompensation': {
                'distance': 'Расстояние',
                'price': 500
            }
        }, ]

    def test_repairs_list(self, *args, **kwargs):
        answer = [
            {
                'date': '10.01.2024 12:02:23',
                'point': 'Тестовая точка 1',
                'serviceman': 'Имя',
                'comments': 'Коментарий',
                'typework':
                [
                    {
                        'typework': 'Работа ремонта',
                        'price': 10
                    }],
                'fuelcompensation':
                {
                    'distance': 'Расстояние',
                    'price': 500
                }}]
        request = client_not_authenticate.get(
            reverse(
                'api:repairs_v2'
            ))
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        request = client_authenticate.get(
            reverse(
                'api:repairs_v2'
            ))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        request_answer = json.loads(request.content)
        self.assertEqual(request_answer, answer)
