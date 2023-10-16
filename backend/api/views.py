import os
from http import HTTPStatus

import httplib2
from coffee_bot_beckend.settings import PATH_TO_ENV
from django.http import JsonResponse
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from points.models import Points
from rest_framework import viewsets

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
POINTS_RANGE = os.getenv('POINTS_RANGE')


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
