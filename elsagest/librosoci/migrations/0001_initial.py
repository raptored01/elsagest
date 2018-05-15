# Generated by Django 2.0.2 on 2018-05-15 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SezioneElsa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('citta', models.TextField()),
            ],
            options={
                'db_table': 'sezioni_elsa',
            },
        ),
        migrations.CreateModel(
            name='Socio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.TextField()),
                ('cognome', models.TextField()),
                ('data_di_nascita', models.DateField()),
                ('codice_fiscale', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('data_iscrizione', models.DateField()),
                ('sezione', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='librosoci.SezioneElsa')),
            ],
            options={
                'db_table': 'soci',
            },
        ),
    ]