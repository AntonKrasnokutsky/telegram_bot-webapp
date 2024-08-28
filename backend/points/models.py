from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Audit(models.Model):
    date = models.DateField(verbose_name='Дата')
    service_man = models.ForeignKey(
        'ServiceMan',
        on_delete=models.PROTECT,
        verbose_name='Исполнитель'
    )
    coffee = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='01. Кофе зерно',
    )
    mokko = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=(
            '031. Капучино Aristocrat Mokka Toffee '
            '1000г (12 шт. в коробке)'
        ),
    )
    cream = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=(
            '02. Заменитель сухих сливок Aristocrat '
            '"Топпинг" 1000г (8 шт. в коробке)'
        ),
    )
    chocolate = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=(
            '03. Горячий шоколад Aristocrat '
            'Классический 1000г (12 шт. в коробке)'
        ),
    )
    raf = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=(
            '04. Смесь сухая "Rapf-coffe" со '
            'вкусом кокоса 1000г (12 шт. в коробке)'
        ),
    )
    sugar = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='05. Сахар порционный 5 г. BLACK (500 шт./кор - 2500 г.)',
    )
    glasses = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='06. Стакан 350 мл. черный (50 шт/уп.)',
    )
    covers = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='07. Крышка для стакана (100 шт./уп.)',
    )
    straws = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=(
            '08. Трубочки коктейльные черные прямые 2*210 (1000 шт./упак)'
        ),
    )
    stirrer = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='09. Размешиватель деревянный 18 см. (250 шт./упак)',
    )
    syrup_caramel = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='10. Сироп "Соленая карамель" (пл. 1л.)',
    )
    syrup_nut = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='11. Сироп "Лесной орех" (пл. 1л.)',
    )


class Points(models.Model):
    name = models.TextField(verbose_name='Название')
    activ = models.BooleanField(default=True)
    tax = models.PositiveIntegerField(default=0, verbose_name='Тариф')

    class Meta:
        ordering = ['name', ]

    def __str__(self, *args, **kwargs):
        return str('*' + self.name if self.activ else self.name)


class ServiceMan(models.Model):
    name = models.TextField()
    telegram_id = models.BigIntegerField(unique=True)
    activ = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return '*' + self.name if self.activ else self.name


class Services(models.Model):
    date = models.DateTimeField(verbose_name='Дата время')
    service_man = models.ForeignKey(
        'ServiceMan',
        on_delete=models.PROTECT,
        verbose_name='Исполнитель'
    )
    point = models.ForeignKey(
        'Points',
        on_delete=models.PROTECT,
        verbose_name='Точка'
    )
    collection = models.PositiveIntegerField(
        default=0,
        verbose_name='Инкасация'
    )
    coffee = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Кофе, кг'
    )
    mokko = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Мокко, кг'
    )
    cream = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Сливки, кг'
    )
    chocolate = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Шоколад, кг'
    )
    raf = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2)
        ],
        verbose_name='Раф, кг'
    )
    sugar = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(250)
        ],
        verbose_name='Сахар, шт'
    )
    syrup_caramel = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп "Соленая карамель", шт'
    )
    syrup_nut = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп "Лесной орех", шт'
    )
    syrup_other = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1)
        ],
        verbose_name='Сироп ДРУГОЙ, шт'
    )
    glasses = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(250)
        ],
        verbose_name='Стаканы, шт'
    )
    covers = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name='Крышки, шт'
    )
    stirrer = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500)
        ],
        verbose_name='Размешиватели, шт'
    )
    straws = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150)
        ],
        verbose_name='Трубочки, шт'
    )
    fuelcompensation = models.ForeignKey(
        'FuelCompensation',
        on_delete=models.PROTECT,
        verbose_name='Компенсация ГСМ',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['date', ]

    def __str__(self, *args, **kwargs):
        return str(self.date)


class Repairs(models.Model):
    date = models.DateTimeField(verbose_name='Дата время')
    service_man = models.ForeignKey(
        'ServiceMan',
        on_delete=models.PROTECT,
        verbose_name='Исполнитель'
    )
    point = models.ForeignKey(
        'Points',
        on_delete=models.PROTECT,
        verbose_name='Точка',
    )
    typework = models.ManyToManyField(
        'TypeWorkRepairs',
        verbose_name='Вид работ',
        blank=True,
    )
    fuelcompensation = models.ForeignKey(
        'FuelCompensation',
        on_delete=models.PROTECT,
        verbose_name='Компенсация ГСМ',
        blank=True,
        null=True,
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий',
    )

    class Meta:
        ordering = ['date', ]

    def __str__(self, *args, **kwargs):
        return f'{self.date} {self.point}'


class TypeWorkRepairs(models.Model):
    typework = models.CharField(max_length=200, verbose_name='Вид работ')
    price = models.PositiveIntegerField(
        default=0,
        verbose_name='Тариф на работу'
    )
    activ = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return f'{str(self.typework)} Тариф: {self.price}'


class FuelCompensation(models.Model):
    distance = models.CharField(max_length=255, verbose_name='Компенсация ГСМ')
    price = models.PositiveIntegerField(default=0, verbose_name='Тариф ГСМ')
    activ = models.BooleanField(default=True)

    def __str__(self, *args, **kwargs):
        return f'{str(self.distance)} Тариф: {self.price}'
