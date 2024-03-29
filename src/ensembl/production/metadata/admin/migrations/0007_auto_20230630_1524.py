# Generated by Django 3.2.19 on 2023-06-30 15:24

from django.db import migrations
import ensembl.production.metadata.admin.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0006_alter_genome_genome_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='dataset_uuid',
            field=ensembl.production.metadata.admin.models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='genome',
            name='genome_uuid',
            field=ensembl.production.metadata.admin.models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
