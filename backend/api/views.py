import json
import os
from datetime import datetime
from http import HTTPStatus

import httplib2
from django.http import JsonResponse
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from points.models import Points
from rest_framework import mixins, permissions, viewsets

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICES = os.getenv('SERVICES')
REPAIRS = os.getenv('REPAIRS')


def get_service_sacc():
    # creds_json = os.path.join(PATH_TO_ENV, CREDENTIALS_FILE)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        # creds_json,
        CREDENTIALS_FILE,
        scopes
    ).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def get_list_points():
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
    return sheet_values


def get_list_services_and_repair(range_value):
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
    return sheet_values


def date_filter(value, date_limite, *args, **kwargs):
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
    return True if record_date <= date_limite['before_date'] else False


def create_answer(values, field_name, date_limit: dict, *args, **kwargs):
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
    return result


def extract_date(request, *args, **kwargs):
    result = {}
    try:
        request_body = json.loads(request.body)
        if 'frome_date' in request_body.keys():
            result['frome_date'] = (
                (
                    datetime.strptime(
                        request_body['frome_date'],
                        '%d.%m.%Y'
                    ).date()))
        if 'before_date' in request_body.keys():
            result['before_date'] = (
                (
                    datetime.strptime(
                        request_body['before_date'],
                        '%d.%m.%Y'
                    ).date()))
    except json.decoder.JSONDecodeError:
        pass

    return result


class PointsViewSet(viewsets.ModelViewSet):
    queryset = Points.objects.all()

    def list(self, *args, **kwargs):
        try:
            points = get_list_points()
        except Exception:
            return JsonResponse(
                {'error': 'Список не обновлен'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        Points.objects.all().delete()
        for name in points:
            Points.objects.create(name=name)
        return JsonResponse(
            {'message': 'Список точек обновлен'},
            status=HTTPStatus.OK
        )


class ServicesViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    # permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        try:
            services = get_list_services_and_repair(SERVICES)
        except Exception:
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        date_limit = extract_date(request)
        return JsonResponse(
            create_answer(services, 'services', date_limit),
            status=HTTPStatus.OK
        )


class RepairViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin):
    # permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        try:
            repairs = get_list_services_and_repair(REPAIRS)
        except Exception:
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        date_limit = extract_date(request)
        return JsonResponse(
            create_answer(repairs, 'repairs', date_limit),
            status=HTTPStatus.OK
        )


class RepairViewASet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        try:
            repairs = get_list_services_and_repair(REPAIRS)
        except Exception:
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        date_limit = extract_date(request)
        return JsonResponse(
            create_answer(repairs, 'repairs', date_limit),
            status=HTTPStatus.OK
        )
