# Generated by Django 3.2.19 on 2024-02-06 16:06

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0015_organism_group_type_enum'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasettype',
            name='depends_on',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='datasettype',
            name='filter_on',
            field=django_mysql.models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='datasettype',
            name='parent',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]