# Generated by Django 4.1 on 2023-09-11 14:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_forecastmodel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecastmodel',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]