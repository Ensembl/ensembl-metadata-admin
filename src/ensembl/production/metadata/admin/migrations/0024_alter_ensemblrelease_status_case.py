"""Fix EnsemblRelease.status choices to match the real DB enum.

Same class of bug as Dataset.status (see 0023): the model stored these as
upper-case ('PLANNED', 'PREPARING', ...) but the real ensembl_release.status
enum is Title-case ('Planned', 'Preparing', 'Prepared', 'Released',
'Archived') - and the model was also missing the 'Archived' value entirely.
State-only since the column type/values are unaffected - only Django's
choices/default metadata changes.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0023_sync_models_with_live_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='ensemblrelease',
                    name='status',
                    field=models.CharField(
                        choices=[
                            ('Planned', 'Planned'),
                            ('Preparing', 'Preparing'),
                            ('Prepared', 'Prepared'),
                            ('Released', 'Released'),
                            ('Archived', 'Archived'),
                        ],
                        default='Planned',
                        max_length=12,
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
