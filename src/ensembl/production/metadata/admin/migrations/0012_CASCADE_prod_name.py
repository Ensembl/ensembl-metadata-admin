# Generated by Django 3.2.19 on 2023-11-17 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0011_is_best_move'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assemblysequence',
            old_name='sha512t4u',
            new_name='sha512t24u',
        ),
        migrations.AddField(
            model_name='genome',
            name='production_name',
            field=models.CharField(default='NA', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organism',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='assemblysequence',
            name='assembly',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.assembly'),
        ),
        migrations.AlterField(
            model_name='datasetattribute',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets_set', to='ensembl_metadata.attribute'),
        ),
        migrations.AlterField(
            model_name='ensemblrelease',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ensembl_metadata.ensemblsite'),
        ),
        migrations.AlterField(
            model_name='genome',
            name='assembly',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.assembly'),
        ),
        migrations.AlterField(
            model_name='genome',
            name='organism',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.organism'),
        ),
        migrations.AlterField(
            model_name='genomedataset',
            name='release',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ensembl_metadata.ensemblrelease'),
        ),
        migrations.AlterField(
            model_name='genomerelease',
            name='genome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.genome'),
        ),
        migrations.AlterField(
            model_name='genomerelease',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.ensemblrelease'),
        ),
        migrations.AlterField(
            model_name='organismgroupmember',
            name='organism',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.organism'),
        ),
        migrations.AlterField(
            model_name='organismgroupmember',
            name='organism_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ensembl_metadata.organismgroup'),
        ),
    ]
