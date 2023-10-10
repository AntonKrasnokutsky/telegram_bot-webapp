import json
from http import HTTPStatus
import base64

from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from points.models import Points
from rest_framework import viewsets

from .serializes import PointsSerializer


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
        print("Go")
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
        name = loads['name']
        data = loads['photo']
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_string = data.split(';base64,')
            ext = format.split('/')[-1]
            image = base64.b64decode(image_string)
            data = ContentFile(
                image,
                name=f'{name}.{ext}'
            )
            print(name)
            
        # print(json.loads(request.body)['name'])

    return HttpResponse('hello')
