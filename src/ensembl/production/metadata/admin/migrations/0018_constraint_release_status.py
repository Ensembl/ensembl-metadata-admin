# Generated by Django 3.2.25 on 2024-03-22 19:21

from django.db import migrations, models
import django.db.models.deletion
import ensembl.production.metadata.admin.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0017_dataset_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='attributes',
            field=models.ManyToManyField(related_name='dataset_attributes', through='ensembl_metadata.DatasetAttribute', to='ensembl_metadata.Attribute'),
        ),
        migrations.AddField(
            model_name='ensemblrelease',
            name='status',
            field=models.CharField(choices=[('PLANNED', 'Planned'), ('PREPARING', 'Preparing'), ('PREPARED', 'Prepared'), ('RELEASED', 'Released')], default='PLANNED', max_length=12),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dataset_uuid',
            field=ensembl.production.metadata.admin.models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='parent',
            field=models.ForeignKey(db_column='parent_id', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.dataset'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='status',
            field=models.CharField(choices=[('SUBMITTED', 'Submitted'), ('PROCESSING', 'Processing'), ('PROCESSED', 'Processed'), ('RELEASED', 'Released')], default='SUBMITTED', max_length=12),
        ),
        migrations.AlterField(
            model_name='datasetattribute',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes_set', to='ensembl_metadata.dataset'),
        ),
        migrations.AlterField(
            model_name='ensemblrelease',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
