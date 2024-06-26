# Generated by Django 3.2.19 on 2023-06-30 15:24

from django.db import migrations, models
import uuid
from ensembl.production.metadata.admin.models import UUIDField


class Migration(migrations.Migration):
    dependencies = [
        ('ensembl_metadata', '0006_alter_genome_genome_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='dataset_uuid',
            field=UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='genome',
            name='genome_uuid',
            field=UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
