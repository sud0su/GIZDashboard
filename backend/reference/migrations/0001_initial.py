# Generated by Django 2.2.10 on 2020-11-23 03:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Incident Source')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Incidient Type')),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Province')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentSubtype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Incident Sub Type')),
                ('incidenttype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.IncidentType', verbose_name='Incident Type')),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='District')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Province', verbose_name='Province')),
            ],
        ),
        migrations.CreateModel(
            name='CityVillage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='City Village')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.District', verbose_name='District')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Province', verbose_name='Province')),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Area Name')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.District', verbose_name='District')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Province', verbose_name='Province')),
            ],
        ),
    ]
