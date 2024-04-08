from django.contrib import admin

from .models import (
    FuelCompensation,
    Points,
    Repairs,
    ServiceMan,
    Services,
    TypeWorkRepairs
)


class ServiceManAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'telegram_id',
        'activ',
    )
    search_fields = ('telegram_id',)
    empty_value_display = '-пусто-'


admin.site.register(Points)
admin.site.register(Repairs)
admin.site.register(Services)
admin.site.register(ServiceMan, ServiceManAdmin)
admin.site.register(TypeWorkRepairs)
admin.site.register(FuelCompensation)
