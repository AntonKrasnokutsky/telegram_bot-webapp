from django.contrib import admin

from .models import (
    Audit,
    ExternalCompanies,
    ExternalRepairs,
    ExternalTypeWorkRepairs,
    FuelCompensation,
    Points,
    Repairs,
    ServiceMan,
    Services,
    TypeWorkRepairs
)


class AuditAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'service_man',
        'date',
    )
    search_fields = ('service_man', 'date')
    empty_value_display = '-пусто-'


class ServiceManAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'telegram_id',
        'activ',
    )
    search_fields = ('telegram_id',)
    empty_value_display = '-пусто-'


class RepairsAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'point',
    )
    empty_value_display = '-пусто-'


class ServicesAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'point',
    )
    empty_value_display = '-пусто-'


class PointsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tax',
        'activ',
    )
    empty_value_display = '-пусто-'


class TypeWorkRepairsAdmin(admin.ModelAdmin):
    list_display = (
        'typework',
        'price',
        'activ',
    )
    empty_value_display = '-пусто-'


class FuelCompensationAdmin(admin.ModelAdmin):
    list_display = (
        'distance',
        'price',
        'activ',
    )
    empty_value_display = '-пусто-'


admin.site.register(Audit, AuditAdmin)
admin.site.register(Points, PointsAdmin)
admin.site.register(Repairs, RepairsAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceMan, ServiceManAdmin)
admin.site.register(TypeWorkRepairs, TypeWorkRepairsAdmin)
admin.site.register(FuelCompensation, FuelCompensationAdmin)

# Ремонт оборудования сторонних компаний
admin.site.register(ExternalCompanies)
admin.site.register(ExternalRepairs)
admin.site.register(ExternalTypeWorkRepairs)
