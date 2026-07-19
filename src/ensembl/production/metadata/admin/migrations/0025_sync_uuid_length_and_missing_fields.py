"""Further fixes found by scripts/check_models_in_sync.py.

- UUIDField declared max_length=36 everywhere, but every *_uuid column in the
  real DB is char(40)/varchar(40); widen it to match exactly.
- ensembl_release.name and genome_release.default are real DB columns that
  were never declared on the Django models at all.

All state-only: the physical columns already exist with these exact shapes.
"""
import uuid

from django.db import migrations, models

import ensembl.production.metadata.admin.models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0024_alter_ensemblrelease_status_case'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='assembly',
                    name='assembly_uuid',
                    field=ensembl.production.metadata.admin.models.UUIDField(
                        default=uuid.uuid4, editable=False, unique=True,
                    ),
                ),
                migrations.AlterField(
                    model_name='organism',
                    name='organism_uuid',
                    field=ensembl.production.metadata.admin.models.UUIDField(
                        default=uuid.uuid4, editable=False, unique=True,
                    ),
                ),
                migrations.AlterField(
                    model_name='genome',
                    name='genome_uuid',
                    field=ensembl.production.metadata.admin.models.UUIDField(
                        default=uuid.uuid4, editable=False, unique=True,
                    ),
                ),
                migrations.AlterField(
                    model_name='dataset',
                    name='dataset_uuid',
                    field=ensembl.production.metadata.admin.models.UUIDField(
                        default=uuid.uuid4, editable=False,
                    ),
                ),
                migrations.AddField(
                    model_name='ensemblrelease',
                    name='name',
                    field=models.CharField(max_length=3, blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='genomerelease',
                    name='default',
                    field=models.BooleanField(default=False),
                ),
            ],
            database_operations=[],
        ),
    ]
