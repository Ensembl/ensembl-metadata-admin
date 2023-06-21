#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.from django.apps import AppConfig
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import SET_NULL


class Assembly(models.Model):
    assembly_id = models.AutoField(primary_key=True)
    ucsc_name = models.CharField(max_length=16, blank=True, null=True)
    accession = models.CharField(unique=True, max_length=16)
    level = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    accession_body = models.CharField(max_length=32, blank=True, null=True)
    assembly_default = models.CharField(max_length=32, blank=True, null=True)
    tol_id = models.CharField(unique=True, max_length=32, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    ensembl_name = models.CharField(unique=True, max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.genome_set.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.genome_set.filter(releases__isnull=False).exists():  # check if it's associated with an EnsemblRelease
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'assembly'
        verbose_name_plural = 'Assemblies'

    def __str__(self):
        return self.name


class AssemblySequence(models.Model):
    assembly_sequence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)
    accession = models.CharField(max_length=128)
    chromosomal = models.IntegerField()
    length = models.IntegerField()
    sequence_location = models.CharField(max_length=10, blank=True, null=True)
    sequence_checksum = models.CharField(max_length=32, blank=True, null=True)
    ga4gh_identifier = models.CharField(max_length=32, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.assembly.genome_set.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.assembly.genome_set.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'assembly_sequence'
        unique_together = (('assembly', 'accession'),)

    def __str__(self):
        return str(self.name)


class Attribute(models.Model):
    ATTRIBUTE_TYPES = [
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('percent', 'Percent'),
        ('string', 'String'),
        ('bp', 'BP'),
    ]
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    label = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8, choices=ATTRIBUTE_TYPES, default='string')

    class Meta:
        db_table = 'attribute'

    def __str__(self):
        return self.name


class DatasetAttribute(models.Model):
    dataset_attribute_id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=128)
    attribute = models.ForeignKey('Attribute', models.DO_NOTHING, related_name='datasets_set')
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, related_name='attributes')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.dataset.genomes.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.dataset.genomes.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'dataset_attribute'
        unique_together = (('dataset', 'attribute', 'value'),)

    def __str__(self):
        return self.attribute.name+':'+self.value


class Dataset(models.Model):
    dataset_id = models.AutoField(primary_key=True)
    dataset_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    dataset_type = models.ForeignKey('DatasetType', models.DO_NOTHING)
    name = models.CharField(max_length=128)
    version = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    dataset_source = models.ForeignKey('DatasetSource', on_delete=models.CASCADE)
    label = models.CharField(max_length=128)
    # attributes = models.ManyToManyField('Attribute', through=DatasetAttribute)
    statuses = [
        ('submitted', 'Submitted'),
        ('progressing', 'Progressing'),
        ('processed', 'Processed'),
    ]

    status = models.CharField(max_length=12, choices=statuses, default='string')
    genomes = models.ManyToManyField('Genome', through='GenomeDataset')

    # genome_datasets = models.ForeignKey('GenomeDataset', on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.genomes.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.genomes.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    def status_value(self):
        return ("%s" % (self.status))


    class Meta:
        db_table = 'dataset'

    def __str__(self):
        return self.name


class DatasetSource(models.Model):
    dataset_source_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=32)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = 'dataset_source'

    def __str__(self):
        return self.name


class DatasetType(models.Model):
    dataset_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    label = models.CharField(max_length=128)
    topic = models.CharField(max_length=32)
    description = models.CharField(max_length=255, blank=True, null=True)
    details_uri = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'dataset_type'

    def __str__(self):
        return self.name


class EnsemblRelease(models.Model):
    release_id = models.AutoField(primary_key=True)
    version = models.DecimalField(max_digits=10, decimal_places=1)
    release_date = models.DateField()
    label = models.CharField(max_length=64, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    site = models.ForeignKey('EnsemblSite', models.DO_NOTHING, blank=True, null=True)
    release_type = models.CharField(max_length=16)
    genomes = models.ManyToManyField('Genome', through='GenomeRelease')
    datasets = models.ManyToManyField('Dataset', through='GenomeDataset')

    class Meta:
        db_table = 'ensembl_release'
        unique_together = (('version', 'site'),)

    def __str__(self):
        return str(self.version)


class EnsemblSite(models.Model):
    site_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    label = models.CharField(max_length=64)
    uri = models.CharField(max_length=64)

    class Meta:
        db_table = 'ensembl_site'

    def __str__(self):
        return self.name


class Genome(models.Model):
    genome_id = models.AutoField(primary_key=True)
    genome_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)
    organism = models.ForeignKey('Organism', models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    datasets = models.ManyToManyField('Dataset', through='GenomeDataset')
    releases = models.ManyToManyField('EnsemblRelease', through='GenomeRelease')

    def save(self, *args, **kwargs):
        if self.pk is not None and self.releases.exists():
            raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.releases.exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'genome'

    def __str__(self):
        return str(self.genome_uuid)


class GenomeDataset(models.Model):
    genome_dataset_id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, models.CASCADE, related_name='genome_datasets')
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE)
    release = models.ForeignKey(EnsemblRelease, models.DO_NOTHING, blank=True, null=True)
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk is not None and self.genome.releases.exists():
            raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.genome.releases.exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'genome_dataset'


class GenomeRelease(models.Model):
    genome_release_id = models.AutoField(primary_key=True)
    genome = models.ForeignKey(Genome, models.DO_NOTHING)
    release = models.ForeignKey(EnsemblRelease, models.DO_NOTHING)
    is_current = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.genome.releases.exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'genome_release'

    def __str__(self):
        return str(self.genome_release_id)


class Organism(models.Model):
    organism_id = models.AutoField(primary_key=True)
    taxonomy_id = models.IntegerField()
    species_taxonomy_id = models.IntegerField(blank=True, null=True)
    display_name = models.CharField(max_length=128)
    strain = models.CharField(max_length=128, blank=True, null=True)
    scientific_name = models.CharField(max_length=128, blank=True, null=True)
    url_name = models.CharField(max_length=128)
    ensembl_name = models.CharField(unique=True, max_length=128)
    scientific_parlance_name = models.CharField(max_length=255, blank=True, null=True)
    groups = models.ManyToManyField('OrganismGroup', through='OrganismGroupMember')
    assemblies = models.ManyToManyField('Assembly', through='Genome')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.genome_set.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.genome_set.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'organism'
        ordering = ['ensembl_name', 'scientific_name']

    def __str__(self):
        return self.ensembl_name


class OrganismGroup(models.Model):
    organism_group_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    code = models.CharField(unique=True, max_length=48, blank=True, null=True)

    class Meta:
        db_table = 'organism_group'
        unique_together = (('type', 'name'),)

    def __str__(self):
        return "Type:" + self.type + " Name:" + self.name


class OrganismGroupMember(models.Model):
    organism_group_member_id = models.AutoField(primary_key=True)
    is_reference = models.BooleanField()
    organism = models.ForeignKey(Organism, models.DO_NOTHING)
    organism_group = models.ForeignKey(OrganismGroup, models.DO_NOTHING)

    class Meta:
        db_table = 'organism_group_member'
        unique_together = (('organism', 'organism_group'),)

    def __str__(self):
        return str(self.organism_group_member_id)
