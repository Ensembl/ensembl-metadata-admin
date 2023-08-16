# Generated by Django 3.2.19 on 2023-08-16 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0008_checksum_general_clean'),
    ]

    operations = [
        migrations.AddField(
            model_name='organism',
            name='strain_type',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='organismgroupmember',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
