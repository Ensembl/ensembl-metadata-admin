"""Add Django models for genome_group, genome_group_member and sequence_alias.

scripts/check_models_in_sync.py's table-coverage check found these three
real, live tables had no Django model at all - not drift in an existing
model, a complete gap in admin coverage. Unlike migrations 0023-0025 this is
a real CREATE... no, these tables already exist physically (confirmed via
DESCRIBE against mysql-ens-automation-test), so this is state-only too:
Django just needs to learn these tables exist.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0025_sync_uuid_length_and_missing_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='SequenceAlias',
                    fields=[
                        ('sequence_alias_id', models.AutoField(primary_key=True, serialize=False)),
                        ('alias', models.CharField(max_length=128)),
                        ('source', models.CharField(blank=True, max_length=128, null=True)),
                        ('assembly_sequence', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            to='ensembl_metadata.assemblysequence',
                        )),
                    ],
                    options={
                        'db_table': 'sequence_alias',
                    },
                ),
                migrations.CreateModel(
                    name='GenomeGroup',
                    fields=[
                        ('genome_group_id', models.AutoField(primary_key=True, serialize=False)),
                        ('type', models.CharField(
                            choices=[
                                ('compara_reference', 'Compara reference'),
                                ('structural_variant', 'Structural variant'),
                                ('project', 'Project'),
                                ('custom', 'Custom'),
                            ],
                            max_length=19,
                        )),
                        ('name', models.CharField(max_length=128)),
                        ('label', models.CharField(max_length=128)),
                        ('searchable', models.BooleanField(default=False)),
                        ('description', models.CharField(blank=True, max_length=255, null=True)),
                    ],
                    options={
                        'db_table': 'genome_group',
                    },
                ),
                migrations.CreateModel(
                    name='GenomeGroupMember',
                    fields=[
                        ('genome_group_member_id', models.AutoField(primary_key=True, serialize=False)),
                        ('is_reference', models.BooleanField(default=False)),
                        ('is_current', models.BooleanField(default=False)),
                        ('genome', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.genome',
                        )),
                        ('genome_group', models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.genomegroup',
                        )),
                        ('release', models.ForeignKey(
                            blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                            to='ensembl_metadata.ensemblrelease',
                        )),
                    ],
                    options={
                        'db_table': 'genome_group_member',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
