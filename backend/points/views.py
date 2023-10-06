from django.shortcuts import render
from django.views import View

from .models import Points


class Service(View):
    template = 'points/service.html'

    def get(self, request, *args, **kwargs):
        points = Points.objects.all()
        context = {
            'points': points,
        }
        return render(
            request,
            self.template,
            context
        )
