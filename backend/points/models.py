from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Points(models.Model):
    name = models.TextField()
    activ = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return str(self.name)


class ServiceMan(models.Model):
    name = models.TextField()
    telegram_id = models.BigIntegerField(unique=True)
    activ = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return self.name


class Services(models.Model):
    date = models.DateTimeField(verbose_name='Дата обслуживания')
    service_man = models.ForeignKey(
        'ServiceMan',
        on_delete=models.PROTECT,
        verbose_name='Инженер'
    )
    point = models.ForeignKey(
        'Points',
        on_delete=models.PROTECT,
        verbose_name='Место'
    )
    collection = models.PositiveIntegerField(
        default=0,
        verbose_name='Сумма инкасации'
    )
    coffee = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Кофе'
    )
    cream = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Сливки'
    )
    chocolate = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Шоколад'
    )
    raf = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Раф'
    )
    sugar = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(250)
        ],
        verbose_name='Сахар'
    )
    syrup_caramel = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп Солёная карамель'
    )
    syrup_nut = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп Лесной орех'
    )
    syrup_other = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп Другой'
    )
    glasses = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(250)
        ],
        verbose_name='Стаканы'
    )
    covers = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name='Крышки'
    )
    stirrer = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500)
        ],
        verbose_name='Размешиватели'
    )
    straws = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150)
        ],
        verbose_name='Трубочки'
    )

    def __str__(self, *args, **kwargs):
        return str(self.date)
