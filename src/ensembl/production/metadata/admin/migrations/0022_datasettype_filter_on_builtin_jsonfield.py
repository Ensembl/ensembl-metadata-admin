from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ensembl_metadata', '0021_auto_20240712_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasettype',
            name='filter_on',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
