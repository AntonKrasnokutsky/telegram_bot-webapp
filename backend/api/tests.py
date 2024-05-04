from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from points.models import ServiceMan

User = get_user_model()
client = APIClient()


class GuestUsersTestCase(TestCase):
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
        client.force_authenticate(cls.test_user)
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

    def test_serviceman(self, *args, **kwargs):
        request = client.get(
            reverse(
                'api:serviceman-list'
            ))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.service_mans), len(request.data))
