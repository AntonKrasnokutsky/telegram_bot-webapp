import os
from http import HTTPStatus

import httplib2
from coffee_bot_beckend.settings import PATH_TO_ENV
from django.http import JsonResponse
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from points.models import Points
from rest_framework import mixins, viewsets

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICES = os.getenv('SERVICES')
REPAIR = os.getenv('REPAIR')


def get_service_sacc():
    creds_json = os.path.join(PATH_TO_ENV, CREDENTIALS_FILE)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json,
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


def create_answer(values, field_name, *args, **kwargs):
    result = {field_name: []}
    pre_result = {}
    for value in values[2:]:
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

    def list(self, request, *args, **kwargs):
        try:
            services = get_list_services_and_repair(SERVICES)
        except Exception:
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        return JsonResponse(
            create_answer(services, 'services'),
            status=HTTPStatus.OK
        )


class RepairViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin):

    def list(self, request, *args, **kwargs):
        try:
            repair = get_list_services_and_repair(REPAIR)
        except Exception:
            return JsonResponse(
                {'error': 'Спиосок не получен. Попробуйте позже'},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        return JsonResponse(
            create_answer(repair, 'repair'),
            status=HTTPStatus.OK
        )
