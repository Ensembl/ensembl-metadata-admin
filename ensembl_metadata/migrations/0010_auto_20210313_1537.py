# Generated by Django 3.1.6 on 2021-03-13 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0009_auto_20210313_1534'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='release',
            name='name',
        ),
        migrations.AddField(
            model_name='release',
            name='label',
            field=models.CharField(max_length=64, null=True),
        ),
    ]