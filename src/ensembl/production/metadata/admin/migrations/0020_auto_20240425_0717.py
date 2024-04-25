# Generated by Django 3.2.25 on 2024-04-25 07:17

from django.db import migrations
import ensembl.production.metadata.admin.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0019_added_genome_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ensemblrelease',
            options={'ordering': ('version',)},
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dataset_uuid',
            field=ensembl.production.metadata.admin.models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
