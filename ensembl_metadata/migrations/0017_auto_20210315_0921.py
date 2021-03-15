# Generated by Django 3.1.6 on 2021-03-15 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0016_delete_genomeattribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='genomebundle',
            name='release_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='genome_bundles', to='ensembl_metadata.release'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dataset',
            name='type',
            field=models.CharField(choices=[('assembly', 'Assembly'), ('xrefs', 'Cross References'), ('dna_alignments', 'Dna Alignments'), ('geneset', 'Geneset'), ('gene_families', 'Gene Families'), ('gene_trees', 'Gene Trees'), ('genome_alignments', 'Genome Alignments'), ('go_terms', 'Go Terms'), ('homologies', 'Homologies'), ('microarrays', 'Microarrays'), ('phenotypes', 'Phenotypes'), ('protein_alignments', 'Protein Alignments'), ('protein_features', 'Protein Features'), ('repeat_features', 'Repeat Features'), ('rnaseq_alignments', 'Rnaseq Alignments'), ('syntenies', 'Syntenies'), ('variants', 'Variants')], max_length=32),
        ),
    ]