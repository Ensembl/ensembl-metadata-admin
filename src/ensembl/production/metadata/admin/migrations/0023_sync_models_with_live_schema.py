"""Reconcile Django's model state with the real ensembl_genome_metadata schema.

The live database (introspected directly via `DESCRIBE`) has drifted from what
these migrations previously recorded: some columns this app's migrations added
were later dropped/moved by other schema owners (e.g. ensembl-metadata-api),
and some columns were added there without ever being reflected here. Every
operation below is state-only (SeparateDatabaseAndState with no database
operations) because the physical columns already match the new state - this
migration only fixes Django's bookkeeping, it does not alter the live table.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0022_datasettype_filter_on_builtin_jsonfield'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # assembly.alt_accession / tol_id / url_name no longer exist;
                # tol_id moved to organism, url_name moved to genome.
                migrations.RemoveField(model_name='assembly', name='alt_accession'),
                migrations.RemoveField(model_name='assembly', name='tol_id'),
                migrations.RemoveField(model_name='assembly', name='url_name'),
                migrations.AddField(
                    model_name='organism',
                    name='tol_id',
                    field=models.CharField(max_length=32, blank=True, null=True),
                ),
                # genome.is_best / genebuild_version no longer exist; genome
                # gained url_name, annotation_source, provider_name,
                # suppressed and suppression_details.
                migrations.RemoveField(model_name='genome', name='is_best'),
                migrations.RemoveField(model_name='genome', name='genebuild_version'),
                migrations.AddField(
                    model_name='genome',
                    name='url_name',
                    field=models.CharField(max_length=128, blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='genome',
                    name='annotation_source',
                    field=models.CharField(max_length=120, default=''),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='genome',
                    name='provider_name',
                    field=models.CharField(max_length=120, default=''),
                    preserve_default=False,
                ),
                migrations.AddField(
                    model_name='genome',
                    name='suppressed',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='genome',
                    name='suppression_details',
                    field=models.CharField(max_length=255, blank=True, null=True),
                ),
                # dataset_type.details_uri / depends_on / filter_on no longer
                # exist; dataset_type gained multiple_current.
                migrations.RemoveField(model_name='datasettype', name='details_uri'),
                migrations.RemoveField(model_name='datasettype', name='depends_on'),
                migrations.RemoveField(model_name='datasettype', name='filter_on'),
                migrations.AddField(
                    model_name='datasettype',
                    name='multiple_current',
                    field=models.BooleanField(default=False),
                ),
                # attribute gained required / required_dataset_type.
                migrations.AddField(
                    model_name='attribute',
                    name='required',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='attribute',
                    name='required_dataset_type',
                    field=models.CharField(max_length=32, blank=True, null=True),
                ),
                # dataset_source gained location.
                migrations.AddField(
                    model_name='datasetsource',
                    name='location',
                    field=models.CharField(max_length=120, blank=True, null=True),
                ),
                # assembly_sequence gained additional / source, and its type
                # enum gained lrg / supscaffold / non_ref_scaffold.
                migrations.AddField(
                    model_name='assemblysequence',
                    name='additional',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='assemblysequence',
                    name='source',
                    field=models.CharField(max_length=120, blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='assemblysequence',
                    name='type',
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ('chromosome_group', 'Chromosome Group'),
                            ('plasmid', 'Plasmid'),
                            ('primary_assembly', 'Primary assembly'),
                            ('contig', 'Contig'),
                            ('chromosome', 'Chromosome'),
                            ('scaffold', 'Scaffold'),
                            ('supercontig', 'Supercontig'),
                            ('lrg', 'LRG'),
                            ('supscaffold', 'Supscaffold'),
                            ('non_ref_scaffold', 'Non-reference scaffold'),
                        ],
                        default='primary_assembly',
                        max_length=26,
                    ),
                ),
                # dataset.status enum values are Title-case in the real DB
                # (Submitted/Processing/...), not upper-case, and also
                # includes Faulty/Suppressed which the model was missing.
                migrations.AlterField(
                    model_name='dataset',
                    name='status',
                    field=models.CharField(
                        choices=[
                            ('Submitted', 'Submitted'),
                            ('Processing', 'Processing'),
                            ('Processed', 'Processed'),
                            ('Released', 'Released'),
                            ('Faulty', 'Faulty'),
                            ('Suppressed', 'Suppressed'),
                        ],
                        default='Submitted',
                        max_length=12,
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
