from django.db import models


class Site(models.Model):
    site_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    label = models.CharField(max_length=64)
    uri = models.CharField(max_length=64)

    class Meta:
        db_table = 'ensembl_site'


class Release(models.Model):
    class ReleaseType(models.TextChoices):
        NIGHTLY = 'nightly'
        PARTIAL = 'partial'
        INTEGRATED = 'integrated'

    release_id = models.AutoField(primary_key=True)
    version = models.IntegerField()
    release_date = models.DateField()
    label = models.CharField(max_length=64, null=True)
    is_current = models.BooleanField(default=False)
    release_type = models.CharField(max_length=16, choices=ReleaseType.choices)
    site = models.ForeignKey(Site, on_delete=models.CASCADE,
                             blank=True, null=True,
                             related_name='releases')

    class Meta:
        db_table = 'ensembl_release'
        unique_together = (('version', 'site'),)

