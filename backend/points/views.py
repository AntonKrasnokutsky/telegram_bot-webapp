import logging
import sys

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from .models import Points, Services

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
            for obj in Points.objects.filter(activ=True)
        ]
        logging.info('Запрос html страницы. Успешно.')
        return context


class ServicesTemplateView(TemplateView):
    template_name = 'points/services_list.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра обслуживаний.')

        context = super().get_context_data(**kwargs)
        services_list = Services.objects.all()
        paginator = Paginator(services_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context
