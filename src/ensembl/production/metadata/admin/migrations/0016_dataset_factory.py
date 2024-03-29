# Generated by Django 3.2.24 on 2024-02-27 20:57

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


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
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='datasettype',
            name='parent',
            field=models.ForeignKey(blank=True, db_column='parent_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ensembl_metadata.datasettype'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='status',
            field=models.CharField(choices=[('Submitted', 'Submitted'), ('Processing', 'Processing'), ('Processed', 'Processed'), ('Released', 'Released')], default='Submitted', max_length=12),
        ),
    ]
