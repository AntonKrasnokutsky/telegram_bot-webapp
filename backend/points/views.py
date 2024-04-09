import logging
import sys

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from api.filters import ServicesFilter

from .forms import FuelCompensationForm, TypeWorkRepairsForm
from .models import (
    FuelCompensation,
    Points,
    Repairs,
    Services,
    TypeWorkRepairs,
)
from .tables import ServiceTable

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class ServicesView(TemplateView):
    template_name = 'points/service.html'

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


class RepairsView(TemplateView):
    template_name = 'points/repair.html'

    def get_context_data(self, **kwargs):
        logging.info('Запрос html страницы.')
        context = super().get_context_data(**kwargs)

        context['points'] = [
            {
                'id': obj.id,
                'value': obj.name,
            }
            for obj in Points.objects.filter(activ=True)
        ]

        context['typework'] = [
            {
                'id': obj.id,
                'value': obj.typework,
            }
            for obj in TypeWorkRepairs.objects.filter(activ=True)
        ]

        context['fuelcompensations'] = [
            {
                'id': obj.id,
                'value': obj.distance,
            }
            for obj in FuelCompensation.objects.filter(activ=True)
        ]

        logging.info('Запрос html страницы. Успешно.')
        return context


class ServicesListView(TemplateView):
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
        context['data'] = [
            {
                'id': obj.id,
                'value': obj.name,
            }
            for obj in Points.objects.filter(activ=True)
        ]
        return context


class RepairsListView(TemplateView):
    template_name = 'points/repairs_list.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра ремонтов.')

        context = super().get_context_data(**kwargs)
        services_list = Repairs.objects.all()
        paginator = Paginator(services_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class TypeWorkRepairsListView(TemplateView):
    template_name = 'points/typeworks.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра видов ремонтов.')

        context = super().get_context_data(**kwargs)
        typework_list = TypeWorkRepairs.objects.filter(activ=True)
        paginator = Paginator(typework_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class TypeWorkRepairsCreateView(View):
    template = 'points/typeworks_create.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def __get_typeworklist(self, *args, **kwargs):
        return [
            {
                'id': obj.id,
                'value': obj.typework,
            }
            for obj in TypeWorkRepairs.objects.filter(activ=True)
        ]

    def get(self, request, *args, **kwargs):
        form = TypeWorkRepairsForm()

        return render(
            request,
            self.template,
            {
                'form': form,
                'typework_list': self.__get_typeworklist(),
            })

    def post(self, request, *args, **kwargs):
        typeworkform = TypeWorkRepairsForm(request.POST)
        if typeworkform.is_valid():
            try:
                logging.info('Ищем работу по ремонту')
                typework = TypeWorkRepairs.objects.get(
                    typework=typeworkform.cleaned_data['typework'],
                    activ=True,
                )
                if typework.price != typeworkform.cleaned_data['price']:
                    logging.info('Вид работ уже внесен. Изменение тарифа.')
                    typework.activ = False
                    typework.save()
                    logging.info('Добавляем новый тариф на работу по ремонту')
                else:
                    logging.info(
                        'Вид работ уже внесен. Изменений не требуется.'
                    )
                    return redirect('points:typeworkrepairs')
            except TypeWorkRepairs.DoesNotExist:
                logging.info('Добавляем новую работу по ремонту')
            typework = typeworkform.save(commit=False)
            typework.active = True
            typework.save()
            return redirect('points:typeworkrepairs')

        return render(
            request,
            self.template,
            {
                'form': typeworkform,
                'typework_list': self.__get_typeworklist(),
            })


class FuelCompensationListView(TemplateView):
    template_name = 'points/fuelcompensation.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра компенсаций топлива.')

        context = super().get_context_data(**kwargs)
        fuelcompensation_list = FuelCompensation.objects.filter(activ=True)
        paginator = Paginator(fuelcompensation_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class FuelCompensationCreateView(View):
    template = 'points/fuelcompensations_create.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def __get_fuelcompensationlist(self, *args, **kwargs):
        return [
            {
                'id': obj.id,
                'value': obj.distance,
            }
            for obj in FuelCompensation.objects.filter(activ=True)
        ]

    def get(self, request, *args, **kwargs):
        form = FuelCompensationForm()

        return render(
            request,
            self.template,
            {
                'form': form,
                'fuelcompensation_list': self.__get_fuelcompensationlist(),
            })

    def post(self, request, *args, **kwargs):
        fuelcompensationform = FuelCompensationForm(request.POST)
        if fuelcompensationform.is_valid():
            try:
                logging.info('Ищем компенсацию ГСМ')
                fuelcompensation = FuelCompensation.objects.get(
                    distance=fuelcompensationform.cleaned_data['distance'],
                    activ=True,
                )
                if (fuelcompensation.price
                   != fuelcompensationform.cleaned_data['price']):
                    logging.info('Компенсация уже внесена. Изменение тарифа.')
                    fuelcompensation.activ = False
                    fuelcompensation.save()
                    logging.info('Добавляем новый тариф компенсации ГСМ')
                else:
                    logging.info(
                        'Компенсация ГСМ уже внесена. Изменений не требуется.'
                    )
                    return redirect('points:fuelcompensations')
            except FuelCompensation.DoesNotExist:
                logging.info('Добавляем новую крмпенсацию ГСМ')
            fuelcompensation = fuelcompensationform.save(commit=False)
            fuelcompensation.active = True
            fuelcompensation.save()
            return redirect('points:fuelcompensations')

        return render(
            request,
            self.template,
            {
                'form': fuelcompensationform,
                'fuelcompensation_list': self.__get_fuelcompensationlist(),
            })


class ServiceListFilteredView(ExportMixin, SingleTableMixin, FilterView):
    model = Services
    table_class = ServiceTable
    export_name = 'services_assistance'
    template_name = 'points/service_list.html'

    filterset_class = ServicesFilter
