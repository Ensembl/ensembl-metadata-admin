# Generated by Django 3.2.25 on 2024-07-12 13:56

from django.db import migrations, models
import ensembl.production.metadata.admin.models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0020_auto_20240425_0717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetattribute',
            name='value',
            field=models.CharField(max_length=255),
        )
    ]
