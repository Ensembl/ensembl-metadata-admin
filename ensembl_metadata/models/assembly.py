from django.db import models


class Assembly(models.Model):
    assembly_id = models.AutoField(primary_key=True)
    accession = models.CharField(unique=True, max_length=16)
    name = models.CharField(max_length=128)
    ucsc_name = models.CharField(max_length=16, blank=True, null=True)
    level = models.CharField(max_length=32)

    class Meta:
        db_table = 'assembly'


class AssemblySequence(models.Model):
    assembly_sequence_id = models.AutoField(primary_key=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='sequences')
    name = models.CharField(max_length=128)
    accession = models.CharField(max_length=32, blank=True, null=True)
    sequence_location = models.CharField(max_length=10, default='SO:0000738', null=True)
    length = models.IntegerField(null=False)
    chromosomal = models.BooleanField(default=False)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    ga4gh_identifier = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'assembly_sequence'
        unique_together = (('assembly', 'name'),)
