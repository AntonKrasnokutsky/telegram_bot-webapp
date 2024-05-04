# Generated by Django 4.2.6 on 2024-05-03 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0006_fuelcompensation_typeworkrepairs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repairs',
            name='category',
        ),
        migrations.RemoveField(
            model_name='repairs',
            name='repair',
        ),
        migrations.AddField(
            model_name='repairs',
            name='fuelcompensation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='points.fuelcompensation', verbose_name='Компенчация ГСМ'),
        ),
        migrations.AddField(
            model_name='repairs',
            name='typework',
            field=models.ManyToManyField(blank=True, to='points.typeworkrepairs', verbose_name='Вид работ'),
        ),
        migrations.AlterField(
            model_name='repairs',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
    ]
