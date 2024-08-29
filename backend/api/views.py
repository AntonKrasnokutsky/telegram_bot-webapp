import json
import logging
import os
import sys
from datetime import datetime
from http import HTTPStatus

import httplib2
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from points.models import Points, Repairs, ServiceMan, Services
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action

from .filters import AuditFilter, RepairsFilter, ServicesFilter
from .serialises import (
    AuditSerializer,
    RepairsSerializer,
    ServiceManSerializer,
    ServicesSerializer,
)

load_dotenv()


CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICES = os.getenv('SHEET_SERVICE')
REPAIRS = os.getenv('SHEET_REPAIRS')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def get_service_sacc():
    logging.info('API: Подключение к Google.')
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        scopes
    ).authorize(httplib2.Http())
    logging.info('API: Подключение к Google. Успешно.')
    return build('sheets', 'v4', http=creds_service)


def get_list_points():
    logging.info('API: Получение списка точек обслуживания.')
    results = get_service_sacc().spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=POINTS_RANGE,
        majorDimension='ROWS',
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING'
    ).execute()
    sheet_values = results['valueRanges'][0]['values']
    try:
        sheet_values.remove('')
    except ValueError:
        pass
    logging.info('API: Получение списка точек обслуживания. Успешно.')
    return sheet_values


def extract_date(request, *args, **kwargs):
    logging.info('API: Поиск ограничений по дате в запросе.')
    result = {}
    try:
        request_body = json.loads(request.body)
        logging.info(
            'API: Поиск ограничений по дате в запросе. '
        )
        if 'frome_date' in request_body.keys():
            result['frome_date'] = (
                datetime.strptime(
                    request_body['frome_date'],
                    '%d.%m.%Y'
                ).date())
            logging.info(
                f'Окраничение по дате с: {result["frome_date"]}'
            )
        if 'before_date' in request_body.keys():
            result['before_date'] = (
                (
                    datetime.strptime(
                        request_body['before_date'],
                        '%d.%m.%Y'
                    ).date()))
            logging.info(
                f'Окраничение по дате по: {result["before_date"]}'
            )
    except json.decoder.JSONDecodeError:
        if len(result) == 0:
            logging.info(
                'Выдаём список за без ограничений.'
            )
    logging.info('API: Поиск ограничений по дате в запросе. Даты выбраны.')
    return result


class PointsViewSet(viewsets.ModelViewSet):
    queryset = Points.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def __deactivate_points(self, *args, **kwargs):
        points = Points.objects.all()
        for point in points:
            point.activ = False
            point.save()

    def list(self, *args, **kwargs):
        logging.info('API: Обновление списка точек.')
        try:
            points = get_list_points()
        except Exception as e:
            logging.error(
                'API: Обновление списка точек. Google недоступен.'
                f'{str(e)}'
            )
            return JsonResponse(
                {'error': 'Список не обновлен'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        self.__deactivate_points()
        for name in points:
            try:
                point = Points.objects.get(name=name[0], tax=name[1])
                point.activ = True
                point.save()
            except Points.DoesNotExist:
                Points.objects.create(name=name[0], tax=name[1])
        logging.info('API: Обновление списка точек. Список точек обновлён.')
        return JsonResponse(
            {'message': 'Список точек обновлен'},
            status=HTTPStatus.OK
        )


class ServicesViewASet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get', 'post']
    serializer_class = ServicesSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = ServicesFilter

    def get_queryset(self):
        date_range = extract_date(self.request)
        if len(date_range) != 0:
            if (
                'frome_date' in date_range.keys()
                and 'before_date' in date_range.keys()
            ):
                return Services.objects.filter(
                    date__gte=date_range['frome_date'],
                    date__lte=date_range['before_date']
                )
            if 'frome_date' in date_range.keys():
                return Services.objects.filter(
                    date__gte=date_range['frome_date']
                )
            return Services.objects.filter(
                date__lte=date_range['before_date']
            )
        return Services.objects.all()


class RepairViewASet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get', 'post']
    serializer_class = RepairsSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RepairsFilter

    def get_queryset(self):
        date_range = extract_date(self.request)
        if len(date_range) != 0:
            if (
                'frome_date' in date_range.keys()
                and 'before_date' in date_range.keys()
            ):
                return Repairs.objects.filter(
                    date__gte=date_range['frome_date'],
                    date__lte=date_range['before_date']
                )
            if 'frome_date' in date_range.keys():
                return Repairs.objects.filter(
                    date__gte=date_range['frome_date']
                )
            return Repairs.objects.filter(
                date__lte=date_range['before_date']
            )
        return Repairs.objects.all()


class ServiceManViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get', 'post']
    serializer_class = ServiceManSerializer
    queryset = ServiceMan.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['telegram_id', ]

    @property
    def service_man(self):
        return get_object_or_404(ServiceMan, pk=self.kwargs.get('pk'))

    @action(
        methods=['post'],
        detail=True,
        url_path='change_activ'
    )
    def change_activ(self, *args, **kwargs):
        service_man = self.service_man
        service_man.activ = not service_man.activ
        service_man.save()

        serializer = ServiceManSerializer(data={
            'id': service_man.id,
            'name': service_man.name,
            'telegram_id': service_man.telegram_id,
            'activ': service_man.activ
        })

        serializer.is_valid()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class AuditViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):

    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post']
    serializer_class = AuditSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = AuditFilter
