# Generated by Django 3.1.7 on 2021-08-11 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0008_auto_20210804_1656'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='datasetattribute',
            unique_together={('dataset', 'attribute', 'type', 'value')},
        ),
    ]
