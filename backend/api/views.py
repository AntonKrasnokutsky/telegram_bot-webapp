import json
from http import HTTPStatus

from django.http import JsonResponse
from points.models import Points
from rest_framework import viewsets

from .serializes import PointsSerializer


class PointsViewSet(viewsets.ModelViewSet):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer

    def create(self, *args, **kwargs):
        Points.objects.all().delete()
        names = json.loads(self.request.data)
        for name in names['names']:
            Points.objects.create(name=name)

        return JsonResponse(names, status=HTTPStatus.CREATED)
