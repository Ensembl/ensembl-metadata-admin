# Generated by Django 3.2.24 on 2024-02-21 09:46

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0016_dataset_type_for_factory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='status',
            field=models.CharField(choices=[('Submitted', 'Submitted'), ('Processing', 'Processing'), ('Processed', 'Processed'), ('Released', 'Released')], default='Submitted', max_length=12),
        ),
        migrations.AlterField(
            model_name='datasettype',
            name='filter_on',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
