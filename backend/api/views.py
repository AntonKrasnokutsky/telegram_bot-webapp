from http import HTTPStatus

from rest_framework import viewsets

from points.models import Points
from .serializes import PointsSerializer
from django.http import JsonResponse


class PointsViewSet(viewsets.ModelViewSet):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer

    def create(self, *args, **kwargs):
        Points.objects.all().delete()
        names = self.request.data
        for name in names['names']:
            Points.objects.create(name=name)

        return JsonResponse(self.request.data, status=HTTPStatus.BAD_REQUEST)


def api_create(request, *args, **kwargs):
    Points.objects.all().delete()
    names = request.data
    print(names)
    for name in names:
        Points.objects.create(name=name)

    return HTTPStatus.CREATED
