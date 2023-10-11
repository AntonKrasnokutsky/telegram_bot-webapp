import json
from http import HTTPStatus
import base64
import os

from django.http import JsonResponse, HttpResponse
from points.models import Points
from rest_framework import viewsets

from .serializes import PointsSerializer
from coffee_bot_beckend.settings import BASE_DIR

PHOTO_LIMIT = 3
PATH_FILE_LIMIT = os.path.join(BASE_DIR, 'photo', 'limit')


def points_api(request, *args, **kwargs):
    methods = ['POST', 'GET', ]
    if request.method not in methods:
        return JsonResponse(
            'Неподдерживаемый тип запроса',
            HTTPStatus.BAD_REQUEST
        )

    if request.method == 'POST':
        Points.objects.all().delete()
        try:
            names = json.loads(request.data)
        except TypeError:
            names = request.data
        for name in names['names']:
            Points.objects.create(name=name)
        points = Points.objects.all()
        result = {
            'names': []
        }
        for point in points:
            result['names'].append(point.name)
        return JsonResponse(result, status=HTTPStatus.CREATED)
    else:
        points = Points.objects.all()
        result = {
            'names': []
        }
        for point in points:
            result['names'].append(point.name)
        return JsonResponse(result, status=HTTPStatus.OK)


class PointsViewSet(viewsets.ModelViewSet):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer

    def create(self, *args, **kwargs):
        Points.objects.all().delete()
        try:
            names = json.loads(self.request.data)
        except TypeError:
            names = self.request.data
        for name in names['names']:
            Points.objects.create(name=name)
        points = Points.objects.all()
        result = {'names': []}
        for point in points:
            result['names'].append(point.name)
        return JsonResponse(result, status=HTTPStatus.CREATED)


def post_image(request):
    if request.method == 'POST':
        loads = json.loads(request.body)
        data = loads['photo']
        if isinstance(data, str) and data.startswith('data:image'):
            with open(PATH_FILE_LIMIT, 'r') as file:
                curent_file = int(file.read())
            curent_file += 1
            if curent_file > PHOTO_LIMIT:
                curent_file = 1
            format, image_string = data.split(';base64,')
            ext = format.split('/')[-1]
            image = base64.b64decode(image_string)
            complete_name = os.path.join(
                BASE_DIR,
                'photo',
                f'photo{curent_file}.{ext}'
            )
            with open(complete_name, 'wb') as file:
                file.write(image)
            with open(PATH_FILE_LIMIT, 'w') as file:
                file.write(str(curent_file))
            return HttpResponse(f'photo{curent_file}.{ext}')
    return HttpResponse(
        'Неподдерживаемый тип запроса',
    )


def get_photo(request, name):
    if request.method == 'GET':
        complete_name = os.path.join(BASE_DIR, 'photo', name)
        if os.path.exists(complete_name) and os.path.isfile(complete_name):
            with open(complete_name, 'rb') as file:
                data = file.read()
            # image = base64.b64encode(data)
            return HttpResponse(data)
        return HttpResponse('Ошибка файла')
    return HttpResponse(
        'Неподдерживаемый тип запроса',
    )
