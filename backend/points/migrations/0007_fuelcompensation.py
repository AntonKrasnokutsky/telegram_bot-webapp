# Generated by Django 4.2.6 on 2024-04-05 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0006_typeworkrepairs'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuelCompensation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.CharField(max_length=255, verbose_name='Компенсация ГСМ')),
                ('price', models.PositiveIntegerField(default=0)),
                ('activ', models.BooleanField(default=True)),
            ],
        ),
    ]