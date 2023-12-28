import logging
import sys

from django.views.generic import TemplateView

from .models import Points

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class SomeTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        logging.info('Запрос html страницы.')
        context = super().get_context_data(**kwargs)

        context['data'] = [
            {
                'id': obj.id,
                'value': obj.name,
            }
            for obj in Points.objects.all()
        ]
        logging.info('Запрос html страницы. Успешно.')
        return context
