# Generated by Django 3.2.25 on 2024-04-04 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0018_constraint_release_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasettype',
            options={'ordering': ['label']},
        ),
        migrations.AddField(
            model_name='genome',
            name='genebuild_date',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='genome',
            name='genebuild_version',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddConstraint(
            model_name='genomedataset',
            constraint=models.UniqueConstraint(fields=('dataset', 'genome'), name='unique_dataset_genome'),
        ),
    ]
