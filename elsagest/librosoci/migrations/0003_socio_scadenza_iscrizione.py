# Generated by Django 2.0.2 on 2018-05-15 20:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('librosoci', '0002_auto_20180515_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='socio',
            name='scadenza_iscrizione',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
