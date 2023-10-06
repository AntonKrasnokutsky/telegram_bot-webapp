import json
from http import HTTPStatus

from django.http import JsonResponse
from points.models import Points


def points_api(request, *args, **kwargs):
    methods = ['POST', 'GET', ]
    if request.method not in methods:
        print("Go")
        return JsonResponse(
            'Неподдерживаемый тип запроса',
            HTTPStatus.METHOD_NOT_ALLOWED
        )
    if request.method == 'POST':
        Points.objects.all().delete()
        try:
            names = json.loads(request.data)
        except TypeError:
            names = request.data
        for name in names['names']:
            Points.objects.create(name=name)

        return JsonResponse(names, status=HTTPStatus.CREATED)
    else:
        points = Points.objects.all()
        result = {
            'names': []
        }
        for point in points:
            result['names'].append(point.name)
        return JsonResponse(result, status=HTTPStatus.OK)
