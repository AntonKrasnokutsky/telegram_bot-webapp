import json
from http import HTTPStatus

from django.http import JsonResponse
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

    # def list(self, *args, **kwargs):
    #     points = Points.objects.all()
    #     # result = PointsSerializer(points, many=True).data
    #     for point in points:
    #         result['names'].append(point.name)
    #     print(result)
    #     return JsonResponse(result, status=HTTPStatus.OK)
