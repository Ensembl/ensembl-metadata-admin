# Generated by Django 3.2.19 on 2023-09-13 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0010_alter_assembly_assembly_default'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genomerelease',
            name='is_best',
        ),
        migrations.AddField(
            model_name='genome',
            name='is_best',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='status',
            field=models.CharField(choices=[('submitted', 'Submitted'), ('progressing', 'Progressing'), ('processed', 'Processed')], default='Submitted', max_length=12),
        ),
    ]