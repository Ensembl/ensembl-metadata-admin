# Generated by Django 3.1.6 on 2021-03-13 15:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0005_auto_20210310_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('bundle_id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, max_length=32, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'bundle',
                'managed': True,
                'unique_together': {('type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('dataset_id', models.AutoField(primary_key=True, serialize=False)),
                ('dataset_uuid', models.CharField(default=uuid.uuid1, max_length=128, unique=True)),
                ('type', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('version', models.CharField(max_length=128, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'dataset',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DatasetDatabase',
            fields=[
                ('dataset_database_id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, max_length=32, null=True)),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'db_table': 'dataset_database',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DatasetRelease',
            fields=[
                ('dataset_release_id', models.AutoField(primary_key=True, serialize=False)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_releases', to='ensembl_metadata.dataset')),
            ],
            options={
                'db_table': 'dataset_release',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DatasetStatistic',
            fields=[
                ('dataset_statistic_id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('value', models.CharField(max_length=128)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='ensembl_metadata.dataset')),
            ],
            options={
                'db_table': 'dataset_statistic',
                'managed': True,
                'unique_together': {('dataset', 'type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='GenomeAttribute',
            fields=[
                ('genome_attribute_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'genome_attribute',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='GenomeBundle',
            fields=[
                ('genome_bundle_id', models.AutoField(primary_key=True, serialize=False)),
                ('is_reference', models.BooleanField(default=False)),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genome_bundles', to='ensembl_metadata.bundle')),
            ],
            options={
                'db_table': 'genome_bundle',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('release_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('version', models.IntegerField()),
                ('release_date', models.DateField()),
                ('is_current', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'release',
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='comparaanalysisevent',
            name='compara_analysis',
        ),
        migrations.AlterUniqueTogether(
            name='datarelease',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='datarelease',
            name='site',
        ),
        migrations.AlterUniqueTogether(
            name='genomealignment',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomealignment',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomealignment',
            name='genome_database',
        ),
        migrations.AlterUniqueTogether(
            name='genomeannotation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomeannotation',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomeannotation',
            name='genome_database',
        ),
        migrations.AlterUniqueTogether(
            name='genomecomparaanalysis',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomecomparaanalysis',
            name='compara_analysis',
        ),
        migrations.RemoveField(
            model_name='genomecomparaanalysis',
            name='genome',
        ),
        migrations.AlterUniqueTogether(
            name='genomedatabase',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomedatabase',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomedivision',
            name='division',
        ),
        migrations.RemoveField(
            model_name='genomedivision',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomeevent',
            name='genome',
        ),
        migrations.AlterUniqueTogether(
            name='genomefeature',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomefeature',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomefeature',
            name='genome_database',
        ),
        migrations.RemoveField(
            model_name='genomerelease',
            name='data_release',
        ),
        migrations.RemoveField(
            model_name='genomerelease',
            name='division',
        ),
        migrations.RemoveField(
            model_name='genomerelease',
            name='genome_uuid',
        ),
        migrations.AlterUniqueTogether(
            name='genomevariation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='genomevariation',
            name='genome',
        ),
        migrations.RemoveField(
            model_name='genomevariation',
            name='genome_database',
        ),
        migrations.RemoveField(
            model_name='organism',
            name='group',
        ),
        migrations.AlterUniqueTogether(
            name='organismalias',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='organismalias',
            name='organism',
        ),
        migrations.RemoveField(
            model_name='organismgroup',
            name='reference_organism',
        ),
        migrations.RenameField(
            model_name='assembly',
            old_name='assembly_accession',
            new_name='accession',
        ),
        migrations.RenameField(
            model_name='assembly',
            old_name='assembly_ucsc',
            new_name='ucsc_name',
        ),
        migrations.RenameField(
            model_name='site',
            old_name='label',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='assembly',
            name='assembly_default',
        ),
        migrations.RemoveField(
            model_name='assembly',
            name='assembly_level',
        ),
        migrations.RemoveField(
            model_name='assembly',
            name='assembly_name',
        ),
        migrations.RemoveField(
            model_name='assemblysequence',
            name='acc',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='created',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='genebuild',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_genome_alignments',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_microarray',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_other_alignments',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_pan_compara',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_peptide_compara',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_synteny',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='has_variation',
        ),
        migrations.RemoveField(
            model_name='genome',
            name='organism',
        ),
        migrations.AddField(
            model_name='assembly',
            name='level',
            field=models.CharField(default='primary', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assembly',
            name='name',
            field=models.CharField(default='name', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assemblysequence',
            name='accession',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='genome',
            name='display_name',
            field=models.CharField(default='display_name', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genome',
            name='ensembl_name',
            field=models.CharField(default='ensembl_name', max_length=128, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genome',
            name='scientific_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='genome',
            name='species_taxonomy_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genome',
            name='strain',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='genome',
            name='taxonomy_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genome',
            name='url_name',
            field=models.CharField(default='url_name', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assemblysequence',
            name='length',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='assemblysequence',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='assemblysequence',
            name='sequence_location',
            field=models.CharField(default='SO:0000738', max_length=10, null=True),
        ),
        migrations.AlterModelTable(
            name='site',
            table='site',
        ),
        migrations.DeleteModel(
            name='ComparaAnalysis',
        ),
        migrations.DeleteModel(
            name='ComparaAnalysisEvent',
        ),
        migrations.DeleteModel(
            name='DataRelease',
        ),
        migrations.DeleteModel(
            name='Division',
        ),
        migrations.DeleteModel(
            name='GenomeAlignment',
        ),
        migrations.DeleteModel(
            name='GenomeAnnotation',
        ),
        migrations.DeleteModel(
            name='GenomeComparaAnalysis',
        ),
        migrations.DeleteModel(
            name='GenomeDatabase',
        ),
        migrations.DeleteModel(
            name='GenomeDivision',
        ),
        migrations.DeleteModel(
            name='GenomeEvent',
        ),
        migrations.DeleteModel(
            name='GenomeFeature',
        ),
        migrations.DeleteModel(
            name='GenomeRelease',
        ),
        migrations.DeleteModel(
            name='GenomeVariation',
        ),
        migrations.DeleteModel(
            name='Organism',
        ),
        migrations.DeleteModel(
            name='OrganismAlias',
        ),
        migrations.DeleteModel(
            name='OrganismGroup',
        ),
        migrations.AddField(
            model_name='release',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='releases', to='ensembl_metadata.site'),
        ),
        migrations.AddField(
            model_name='genomebundle',
            name='genome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genome_bundles', to='ensembl_metadata.genome'),
        ),
        migrations.AddField(
            model_name='genomeattribute',
            name='genome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='ensembl_metadata.genome'),
        ),
        migrations.AddField(
            model_name='datasetrelease',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_releases', to='ensembl_metadata.release'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='dataset_database',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='ensembl_metadata.datasetdatabase'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='genome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='ensembl_metadata.genome'),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together={('version', 'site')},
        ),
        migrations.AlterUniqueTogether(
            name='genomebundle',
            unique_together={('genome', 'bundle')},
        ),
        migrations.AlterUniqueTogether(
            name='genomeattribute',
            unique_together={('genome', 'name')},
        ),
    ]