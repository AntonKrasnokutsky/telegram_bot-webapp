import json
import logging
import os
import sys
from datetime import datetime, timedelta
from http import HTTPStatus

import httplib2
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from points.models import Points
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import action

from points.models import Services, ServiceMan
from .filters import ServicesFilter
from .serialises import ServicesSerializer, ServiceManSerializer

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICES = os.getenv('SHEET_SERVICE')
REPAIRS = os.getenv('SHEET_REPAIRS')
days_to_subtract = 7

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
        majorDimension='COLUMNS',
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING'
    ).execute()
    sheet_values = results['valueRanges'][0]['values'][0]
    try:
        sheet_values.remove('')
    except ValueError:
        pass
    logging.info('API: Получение списка точек обслуживания. Успешно.')
    return sheet_values


def get_list_services_and_repair(range_value):
    logging.info('API: Получение списка обслуживаний или ремонтов.')
    results = get_service_sacc().spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=range_value,
        majorDimension='ROWS',
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING'
    ).execute()
    sheet_values = results['valueRanges'][0]['values']
    try:
        sheet_values.remove('')
    except ValueError:
        pass
    logging.info('API: Получение списка обслуживаний или ремонтов. Успешно.')
    return sheet_values


def date_filter(value, date_limite, *args, **kwargs):
    logging.info('API: Фильтр списка обслуживаний или ремонтов по датам.')
    record_date = datetime.strptime(
        value[0],
        '%d.%m.%Y %H:%M:%S'
    ).date()
    if ('frome_date' in date_limite.keys()
            and 'before_date' in date_limite.keys()):
        return (
            True
            if (date_limite['frome_date'] <= record_date
                and record_date <= date_limite['before_date'])
            else False
        )
    elif 'frome_date' in date_limite.keys():
        return True if date_limite['frome_date'] <= record_date else False

    logging.info(
        'API: Фильтр списка обслуживаний или ремонтов по датам. Успешно.'
    )

    return True if record_date <= date_limite['before_date'] else False


def create_answer(values, field_name, date_limit: dict, *args, **kwargs):
    logging.info('API: Подготовка ответного сообщения на запрос.')
    result = {field_name: []}
    pre_result = {}
    for pos in range(len(values[0])):
        values[0][pos] = values[0][pos].translate(
            {
                ord(','): None,
                ord('"'): None,
                ord("'"): None,
                ord(' '): None
            })
    for value in values[2:]:
        if len(date_limit) != 0:
            if not date_filter(value, date_limit):
                continue
        for pos in range(len(value)):
            if '₽\xa0 ' in value[pos]:
                pre_result[values[0][pos]] = value[pos].translate(
                    {
                        ord('\xa0'): None,
                        ord('₽'): None,
                        ord(' '): None
                    })
            else:
                pre_result[values[0][pos]] = value[pos]
        result[field_name].append(pre_result.copy())
    logging.info('API: Подготовка ответного сообщения на запрос. Успешно.')
    return result


def extract_date(request, *args, **kwargs):
    logging.info('API: Поиск ограничений по дате в запросе.')
    result = {}
    try:
        request_body = json.loads(request.body)
        if 'frome_date' in request_body.keys():
            result['frome_date'] = (
                datetime.strptime(
                    request_body['frome_date'],
                    '%d.%m.%Y'
                ).date())
        if 'before_date' in request_body.keys():
            result['before_date'] = (
                (
                    datetime.strptime(
                        request_body['before_date'],
                        '%d.%m.%Y'
                    ).date()))
    except json.decoder.JSONDecodeError:
        result['frome_date'] = (
            datetime.today()
            - timedelta(days=days_to_subtract)
        )
        logging.info(
            'API: Поиск ограничений по дате в запросе. '
            'Выдаём список за 7 дней.'
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
        except Exception:
            logging.error('API: Обновление списка точек. Google недоступен.')
            return JsonResponse(
                {'error': 'Список не обновлен'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        self.__deactivate_points()
        for name in points:
            try:
                point = Points.objects.get(name=name)
                point.activ = True
                point.save()
            except Points.DoesNotExist:
                Points.objects.create(name=name)
        logging.info('API: Обновление списка точек. Список точек обновлён.')
        return JsonResponse(
            {'message': 'Список точек обновлен'},
            status=HTTPStatus.OK
        )


class ServicesViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        logging.info('API: Запрос списка обслуживний.')
        try:
            services = get_list_services_and_repair(SERVICES)
        except Exception:
            logging.error('API: Запрос списка обслуживний. Google недоступен.')
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        logging.info('API: Запрос списка обслуживний. Успешно.')
        return JsonResponse(
            create_answer(
                services,
                'services',
                extract_date(request)
            ),
            status=HTTPStatus.OK
        )


class RepairViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        logging.info('API: Запрос списка ремонтров.')
        try:
            repairs = get_list_services_and_repair(REPAIRS)
        except Exception:
            logging.info('API: Запрос списка ремонтров. Google недоступен.')
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        logging.info('API: Запрос списка ремонтров. Успешно.')
        return JsonResponse(
            create_answer(
                repairs,
                'repairs',
                extract_date(request)
            ),
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
    filter_backends = (DjangoFilterBackend, )
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


class RepairViewASet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        logging.info('API(авторизация): Запрос списка ремонтров.')
        try:
            repairs = get_list_services_and_repair(REPAIRS)
        except Exception:
            logging.error(
                'API(авторизация): Запрос списка ремонтров. Google недоступен.'
            )
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        logging.info('API(авторизация): Запрос списка ремонтров. Успешно.')
        return JsonResponse(
            create_answer(
                repairs,
                'repairs',
                extract_date(request)
            ),
            status=HTTPStatus.OK
        )


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
