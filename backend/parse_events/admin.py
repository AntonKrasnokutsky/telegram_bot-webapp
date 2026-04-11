from django.contrib import admin

from .models import Events, EventsOfDay, EventsOfPoints

class EventsAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'used',
    )
    list_filter = ('used',)
    search_fields = ('event',)
    empty_value_display = '-пусто-'

class EventsOfDayAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'event',
    )
    list_filter = ('date',)
    search_fields = ('event', 'date')
    empty_value_display = '-пусто-'

class EventsOfPointsAdmin(admin.ModelAdmin):
    list_display = (
        'point',
    )
    search_fields = ('point',)
    empty_value_display = '-пусто-'

admin.site.register(Events, EventsAdmin)
admin.site.register(EventsOfDay, EventsOfDayAdmin)
admin.site.register(EventsOfPoints, EventsOfPointsAdmin)
