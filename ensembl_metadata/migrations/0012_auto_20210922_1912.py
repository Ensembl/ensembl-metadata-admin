# Generated by Django 3.1.7 on 2021-09-22 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0011_auto_20210907_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='genomedataset',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='genomerelease',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='release',
            name='release_type',
            field=models.CharField(choices=[('nightly', 'Nightly'), ('partial', 'Partial'), ('integrated', 'Integrated')], max_length=16),
        ),
    ]
