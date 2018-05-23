# Generated by Django 2.0.2 on 2018-05-23 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('librosoci', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BozzaEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oggetto', models.TextField()),
                ('corpo', models.TextField()),
                ('creata_il', models.DateTimeField(auto_now_add=True)),
                ('disponibile_per', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oggetto', models.TextField()),
                ('corpo', models.TextField()),
                ('inviata_il', models.DateTimeField(auto_now_add=True)),
                ('mittente', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UnsubscribeToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.UUID('1e038752-779a-4cae-9b2a-1b0f52ef11a1'), editable=False)),
                ('socio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='librosoci.Socio')),
            ],
        ),
    ]
