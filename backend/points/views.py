import logging
import sys

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from api.filters import (
    AuditFilter,
    ExternalRepairsFilter,
    RepairsFilter,
    ServicesFilter,
)

from .exports import (
    AuditTableExport,
    ExtarnalRepairsTableExport,
    RepairsTableExport,
)
from .forms import (
    ExternalCompaniesForm,
    ExternalTypeWorkRepairsForm,
    FuelCompensationForm,
    TypeWorkRepairsForm
)
from .models import (
    Audit,
    ExternalCompanies,
    ExternalRepairs,
    ExternalTypeWorkRepairs,
    FuelCompensation,
    Points,
    Repairs,
    Services,
    ServiceMan,
    TypeWorkRepairs,
)
from .tables import (
    AuditTable,
    ExternalRepairsTable,
    RepairsTable,
    ServiceTable,
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class ServicesView(TemplateView):
    template_name = 'points/service.html'

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

        context['fuelcompensations'] = [
            {
                'id': obj.id,
                'value': obj.distance,
            }
            for obj in FuelCompensation.objects.filter(activ=True)
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

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_mans'] = ServiceMan.objects.all()
        context['points'] = Points.objects.all()
        return context


class RepairsListFilteredView(ExportMixin, SingleTableMixin, FilterView):
    model = Repairs
    table_class = RepairsTable
    export_name = 'repairs_assistance'
    template_name = 'points/repairs_list.html'
    export_class = RepairsTableExport

    filterset_class = RepairsFilter

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AuditView(TemplateView):
    template_name = 'points/audit.html'


class AuditListFilteredView(ExportMixin, SingleTableMixin, FilterView):
    model = Audit
    table_class = AuditTable
    export_name = 'audit_assistance'
    template_name = 'points/audit_list.html'
    export_class = AuditTableExport

    filterset_class = AuditFilter

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# Ремонт оборудования сторонних компаний
class ExternalCompaniesListView(TemplateView):
    template_name = 'points/external/companies/company_list.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра внешних компаний.')

        context = super().get_context_data(**kwargs)
        externalcompanies_list = ExternalCompanies.objects.all()
        paginator = Paginator(externalcompanies_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ExternalCompaniesCreateView(View):
    template = 'points/external/companies/company_create.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        logging.info('Запрос формы добавления внешней компании')
        return render(
            request,
            self.template,
            {
                'form': ExternalCompaniesForm(),
            })

    def post(self, request, *args, **kwargs):
        externalcompany_form = ExternalCompaniesForm(request.POST)
        if externalcompany_form.is_valid():
            logging.info('Добавляем новую внешнюю компанию')
            externalcompany = externalcompany_form.save(commit=False)
            externalcompany.active = True
            externalcompany.save()
            logging.info('Новая внешня компания добавлена')
            return redirect('points:externalcompany')
        logging.info('Ошибки в форме добавления внешней компании')
        return render(
            request,
            self.template,
            {
                'form': externalcompany_form,
            })


class ExternalCompaniesChangeActivView(View):
    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        logging.info('Изменение статуса активности внешней компании')
        externalcompany = get_object_or_404(
            ExternalCompanies,
            pk=kwargs['company_id']
        )
        externalcompany.activ = not externalcompany.activ
        externalcompany.save()
        return redirect('points:externalcompany')


class ExternalTypeWorkRepairsListVies(TemplateView):
    template_name = 'points/external/typework/typework_list.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        logging.info('Запрос страницы просмотра внешних видов работ.')

        context = super().get_context_data(**kwargs)
        externaltypework_list = ExternalTypeWorkRepairs.objects.filter(
            activ=True
        )
        paginator = Paginator(externaltypework_list, 20)
        page_number = self.request.GET.get('page', paginator.num_pages)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ExternalTypeWorkRepairsCreateView(View):
    template = 'points/external/typework/typework_create.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def __get_externaltypeworklist(self, *args, **kwargs):
        return [
            {
                'id': obj.id,
                'value': obj.typework,
            }
            for obj in ExternalTypeWorkRepairs.objects.filter(activ=True)
        ]

    def get(self, request, *args, **kwargs):
        logging.info('Запрос страницы добавления внешних видов работ.')
        form = ExternalTypeWorkRepairsForm()

        return render(
            request,
            self.template,
            {
                'form': form,
                'externaltypework_list': self.__get_externaltypeworklist(),
            })

    def post(self, request, *args, **kwargs):
        logging.info('Добавление внешнего вида работ.')
        externaltypeworkform = ExternalTypeWorkRepairsForm(request.POST)
        if externaltypeworkform.is_valid():
            try:
                logging.info('Ищем внешний вид работ')
                externaltypework = ExternalTypeWorkRepairs.objects.get(
                    typework=externaltypeworkform.cleaned_data['typework'],
                    activ=True,
                )
                if (externaltypework.price
                   != externaltypeworkform.cleaned_data['price']):
                    logging.info(
                        'Внешний вид работ уже внесён.'
                        ' Изменение тарифа.'
                    )
                    externaltypework.activ = False
                    externaltypework.save()
                    logging.info('Добавляем новый тариф внешнего вида работ')
                else:
                    logging.info(
                        'Внешний вид работ уже внесён. Изменений не требуется.'
                    )
                    return redirect('points:externaltypeworks_list')
            except ExternalTypeWorkRepairs.DoesNotExist:
                logging.info('Добавляем новый вид внешних работ')
            externaltypework = externaltypeworkform.save(commit=False)
            externaltypework.active = True
            externaltypework.save()
            return redirect('points:externaltypeworks_list')

        return render(
            request,
            self.template,
            {
                'form': externaltypeworkform,
                'externaltypework_list': self.__get_externaltypeworklist(),
            })


class ExternalRepairsView(TemplateView):
    template_name = 'points/external/external_repair.html'

    def get_context_data(self, **kwargs):
        logging.info('Запрос html страницы для внешних компаний.')
        context = super().get_context_data(**kwargs)

        context['companies'] = [
            {
                'id': obj.id,
                'value': obj.company_name,
            }
            for obj in ExternalCompanies.objects.filter(activ=True)
        ]

        context['typework'] = [
            {
                'id': obj.id,
                'value': obj.typework,
            }
            for obj in ExternalTypeWorkRepairs.objects.filter(activ=True)
        ]

        logging.info('Запрос html страницы для внешних компаний. Успешно.')
        return context


class ExternalRepairsListFilteredView(
    ExportMixin,
    SingleTableMixin,
    FilterView
):
    model = ExternalRepairs
    table_class = ExternalRepairsTable
    export_name = 'external_repairs_assistance'
    template_name = 'points/external/external_repairs_list.html'
    export_class = ExtarnalRepairsTableExport

    filterset_class = ExternalRepairsFilter

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
