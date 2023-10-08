# from django.shortcuts import render
# from django.views import View

from .models import Points


# class Service(View):
#     template = 'points/service.html'

#     def get(self, request, *args, **kwargs):
#         points = Points.objects.all()
#         context = {
#             'data': {
#                 'value': obj.name,
#             }
#             for obj in Points.objects.all()
#             # 'points': points,
#         }
#         return render(
#             request,
#             self.template,
#             context
#         )
from django.views.generic import TemplateView


class SomeTemplateView(TemplateView):
    template_name = 'points/service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['data'] = [
            {
                'id': obj.id,
                'value': obj.name,
            }
            for obj in Points.objects.all()
        ]

        return context
