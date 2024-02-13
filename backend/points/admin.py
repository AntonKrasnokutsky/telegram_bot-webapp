from django.contrib import admin

from .models import Points, Services, ServiceMan


class ServiceManAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'telegram_id',
    )
    search_fields = ('telegram_id',)
    empty_value_display = '-пусто-'


admin.site.register(Points)
admin.site.register(Services)
admin.site.register(ServiceMan, ServiceManAdmin)
