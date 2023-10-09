from django.views.generic import TemplateView

from .models import Points


class SomeTemplateView(TemplateView):
    # template_name = 'points/service.html'

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
