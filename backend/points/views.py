import datetime
import logging
import sys
import zoneinfo

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    ExternalRepairsServiceManFilter,
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
    ExtermalWorkInRepairs,
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
    ExternalRepairsManTable,
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)


# Ремонт оборудования сторонних компаний
class ExternalCompaniesListView(TemplateView):
    template_name = 'points/external/companies/company_list.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
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
        if (
            not self.request.user.is_superuser
        ):
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)


class ExternalRepairsSalaryView(TemplateView):
    template_name = 'points/external/external_repair_salary.html'

    def get_context_data(self, **kwargs):
        logging.info('Запрос html страницы с датами заплаты. Успешно.')
        return super().get_context_data(**kwargs)


class ExternalRepairsWebView(View):
    template_name = 'points/external/external_repair_web.html'

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        logging.info('Добавление внешних работ.')
        if (
            not self.request.user.is_staff
            or not self.request.user.userprofile.office_engineer
            or self.request.user.userprofile.telegram_id is None
        ):

            logging.info('Пользователю запрещено заполнение формы.')
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)

    def __prepare_context(self, error=None) -> dict:
        context = {}
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
        if error:
            context['error'] = error
        return context

    def get(self, *args, **kwargs):
        logging.info('Запрос html страницы для внешних компаний. Успешно.')

        return render(
            self.request,
            self.template_name,
            self.__prepare_context(),
        )

    def __get_company(self) -> ExternalCompanies | bool:
        try:
            logging.info('Поиск компании.')
            company = ExternalCompanies.objects.get(
                company_name=self.request.POST['company_name']
            )
        except ExternalCompanies.DoesNotExist:
            logging.info(
                'Компании с названием: \"'
                f'{self.request.POST["company_name"]}'
                '\" не сущетвует.'
            )
            return False
        logging.info(
            'Компания с названием: \"'
            f'{self.request.POST["company_name"]}'
            '\" найдена.'
        )
        return company

    def __get_works(self) -> list | bool:
        result = []
        works = {
            k: self.request.POST[k]
            for k in self.request.POST.dict().keys()
            if k.startswith('work')
        }
        logging.info('Подготовка списка работ.')
        for pos in range(1, len(works) // 2 + 1):
            try:
                logging.info(f'Поиск вида работ: \"{works[f"work_{pos}"]}\".')
                work = {
                    'work': ExternalTypeWorkRepairs.objects.get(
                        typework=str(works[f'work_{pos}']),
                        activ=True,
                    ),
                    'count': int(works[f'work_{pos}_count']),
                }
            except ExternalTypeWorkRepairs.DoesNotExist:
                logging.info(
                    'Вида работ: \"'
                    f'{works[f"work_{pos}"]}'
                    '\" не сущетвует.'
                )
                return False
            result.append(work)
        if len(result) == 0:
            logging.info('Список работ пуст.')
        else:
            logging.info(f'Список из {len(result)} работ подготовлен.')
        return result

    def __get_service_man(self) -> ServiceMan | bool:
        logging.info(
            'Поиск инженера по telegram_id: \"'
            f'{self.request.user.userprofile.telegram_id}'
            '\".'
        )
        try:
            service_man = ServiceMan.objects.get(
                telegram_id=self.request.user.userprofile.telegram_id,
                activ=True
            )
        except ServiceMan.DoesNotExist:
            logging.info(
                'Инженера с telegram_id: \"'
                f'{self.request.user.userprofile.telegram_id}'
                '\" не сущетвует.'
            )
            return False
        logging.info(
            'Инженер с telegram_id: \"'
            f'{self.request.user.userprofile.telegram_id}'
            '\" найден.'
        )
        return service_man

    def __prepare_data(self) -> dict | bool:
        result = {
            'company': self.__get_company(),
            'serial_num': str(self.request.POST['serial_num_coffe']),
            'comment': str(self.request.POST['comment']),
            'works': self.__get_works(),
            'service_man': self.__get_service_man(),
        }
        if (
            not result['company']
            or isinstance(result['works'], bool)
            or not result['service_man']
        ):
            print('Сохранять нечего')
            return False
        return result

    def __save_data(self, data: dict) -> None:
        logging.info('Добавление записи о внешнем ремонте.')
        external_repair = ExternalRepairs.objects.create(
            company=data['company'],
            serial_num_coffe=data['serial_num'],
            service_man=data['service_man'],
            comments=data['comment'],
            date=datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Moscow")),
        )
        logging.info('Добавление записи о работах во внешнем ремонте.')

        for work in data['works']:
            ExtermalWorkInRepairs.objects.create(
                external_repair=external_repair,
                external_work=work['work'],
                count=work['count'],
            )

    def post(self, *args, **kwargs):
        external_works = self.__prepare_data()
        if external_works:
            self.__save_data(external_works)
            return redirect('points:external_man_list')

        return render(
            self.request,
            self.template_name,
            self.__prepare_context(),
        )


class ExternalRepairsListServiceMan(
    SingleTableMixin,
    FilterView
):
    model = ExternalRepairs
    table_class = ExternalRepairsManTable
    template_name = 'points/external/external_repairs_servoce_man_list.html'

    filterset_class = ExternalRepairsServiceManFilter

    @method_decorator(login_required(login_url='users:login'))
    def dispatch(self, *args, **kwargs):
        logging.info('Добавление внешних работ.')
        if (
            not self.request.user.is_staff
            or not self.request.user.userprofile.office_engineer
            or self.request.user.userprofile.telegram_id is None
        ):

            logging.info('Пользователю запрещено заполнение формы.')
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        service_man = ServiceMan.objects.get(
            activ=True,
            telegram_id=self.request.user.userprofile.telegram_id
        )
        return ExternalRepairs.objects.filter(service_man=service_man)

    def __calculate(self, object_list):
        salary = 0
        for external_repair in object_list:
            for work in external_repair.types_work.all():
                salary += work.external_work.price * work.count

        return salary if salary else 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calculate'] = self.__calculate(kwargs['object_list'])
        return context
