from django.db import models

from points.models import Points


class Events(models.Model):
    event = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Событие',
    )
    used = models.BooleanField(
        default=True,
        verbose_name='Отслеживается',
    )

    class Meta:
        ordering = ['event', ]
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
    
    def __str__(self):
        return self.event


class EventsOfDay(models.Model):
    event = models.ForeignKey(
        'Events',
        on_delete=models.PROTECT,
        verbose_name='Событие',
    )
    count = models.PositiveSmallIntegerField(verbose_name='Количество событий')
    date = models.DateField(verbose_name='Дата события')

    class Meta:
        ordering = ['-date', 'event',]
        verbose_name = 'Собитие дня'
        verbose_name_plural = 'События дней'
    
    def __str__(self):
        return str(self.event)


class EventsOfPoints(models.Model):
    point = models.ForeignKey(
        Points,
        on_delete=models.PROTECT,
        verbose_name='Точка обслуживания',
    )
    events = models.ManyToManyField(
        EventsOfDay,
        verbose_name='События',
        # through='EventsPointsOfDay',
        # blank=True,
    )

    class Meta:
        ordering = ['point',]
        verbose_name = 'Событие точки'
        verbose_name_plural = 'События точек'
    
    def __str__(self):
        return str(self.point)

# class EventsPointsOfDay(models.Model):
#     event_point = models.ForeignKey(
#         EventsOfPoints,
#         on_delete=models.PROTECT,
#         verbose_name='Точка обслуживания',
#     )
#     event = models.ForeignKey(
#         'EventsOfDay',
#         on_delete=models.CASCADE,
#         verbose_name='Событие',
#     )

#     class Meta:
#         ordering = ['event_point', 'event', ]
#         verbose_name = 'Событие точки'
#         verbose_name_plural = 'События точек'

#     def __str__(self):
#         return self.event.event
