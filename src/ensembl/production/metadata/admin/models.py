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

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.lookups import IContains
from django_mysql.models import JSONField


class UUIDField(models.UUIDField):

    def __init__(self, verbose_name=None, **kwargs):
        super().__init__(verbose_name, **kwargs)
        self.max_length = 40

    def get_internal_type(self):
        return "CharField"

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value)
            except AttributeError:
                raise TypeError(self.error_messages['invalid'] % {'value': value})

        if connection.features.has_native_uuid_field:
            return value
        return str(value)


@UUIDField.register_lookup
class UUIDIContains(IContains):
    pass


class Assembly(models.Model):
    assembly_id = models.AutoField(primary_key=True)
    ucsc_name = models.CharField(max_length=16, blank=True, null=True)
    accession = models.CharField(unique=True, max_length=16)
    alt_accession = models.CharField(max_length=16, null=True)
    level = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    accession_body = models.CharField(max_length=32, blank=True, null=True)
    assembly_default = models.CharField(max_length=128, blank=True, null=True)
    tol_id = models.CharField(unique=True, max_length=32, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    ensembl_name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    assembly_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_reference = models.BooleanField(default=False, null=False)
    url_name = models.CharField(max_length=128, null=True)

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
    class SequenceType(models.TextChoices):
        CHROM_GROUP = 'chromosome_group', 'Chromosome Group'
        PLASMID = 'plasmid', 'Plasmid'
        PRIMARY = 'primary_assembly', 'Primary assembly'
        CONTIG = 'contig', 'Contig'
        CHROMOSOME = 'chromosome', 'Chromosome'
        SCAFFOLD = 'scaffold', 'Scaffold'
        SUPERCONTIG = 'supercontig', 'Supercontig'

    assembly_sequence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    accession = models.CharField(max_length=128)
    chromosomal = models.BooleanField()
    chromosome_rank = models.IntegerField(blank=True, null=True)
    length = models.IntegerField()
    sequence_location = models.CharField(max_length=10, blank=True, null=True)
    md5 = models.CharField(max_length=32, blank=True, null=True)
    sha512t24u = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(choices=SequenceType.choices, max_length=26, blank=True, null=False, default=SequenceType.PRIMARY)
    is_circular = models.BooleanField(null=False, default=False)

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
    class AttributeType(models.TextChoices):
        integer = 'integer', 'Integer'
        float = 'float', 'Float'
        percent = 'percent', 'Percent'
        string = 'string', 'String'
        bp = 'bp', 'BP'

    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    label = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8, choices=AttributeType.choices, default='string')

    class Meta:
        db_table = 'attribute'

    def __str__(self):
        return self.name


class Dataset(models.Model):
    dataset_id = models.AutoField(primary_key=True)
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
    status = models.CharField(max_length=12, choices=statuses, default='Submitted')
    genomes = models.ManyToManyField('Genome', through='GenomeDataset')
    dataset_type = models.ForeignKey('DatasetType', models.DO_NOTHING)
    dataset_uuid = UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        db_table = 'dataset'

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
        return f"{self.status}"

    def __str__(self):
        return self.name


class DatasetAttribute(models.Model):
    dataset_attribute_id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=128)
    attribute = models.ForeignKey('Attribute', on_delete=models.CASCADE, related_name='datasets_set')
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, related_name='attributes')

    class Meta:
        db_table = 'dataset_attribute'
        unique_together = (('dataset', 'attribute', 'value'),)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.dataset.genomes.filter(releases__isnull=False).exists():
                raise ValidationError('Released data cannot be modified')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.dataset.genomes.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.attribute.name + ':' + self.value


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
    parent = models.CharField(max_length=128, blank=True, null=True)
    depends_on = models.CharField(max_length=128, blank=True, null=True)
    filter_on = JSONField(blank=True, null=True)  # JSON field

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
    site = models.ForeignKey('EnsemblSite', on_delete=models.SET_NULL, blank=True, null=True)
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
    genome_uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    organism = models.ForeignKey('Organism', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_best = models.BooleanField(default=False)
    datasets = models.ManyToManyField('Dataset', through='GenomeDataset')
    releases = models.ManyToManyField('EnsemblRelease', through='GenomeRelease')
    production_name = models.CharField(max_length=255)

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

    def __repr__(self):
        return str(self.genome_uuid)


class GenomeDataset(models.Model):
    genome_dataset_id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='genome_datasets')
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE)
    release = models.ForeignKey(EnsemblRelease, on_delete=models.SET_NULL, blank=True, null=True)
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
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE)
    release = models.ForeignKey(EnsemblRelease, on_delete=models.CASCADE)
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
    common_name = models.CharField(max_length=128)
    strain = models.CharField(max_length=128, blank=True, null=True)
    scientific_name = models.CharField(max_length=128, blank=True, null=True)
    biosample_id = models.CharField(unique=True, null=False, max_length=128)
    scientific_parlance_name = models.CharField(max_length=255, blank=True, null=True)
    groups = models.ManyToManyField('OrganismGroup', through='OrganismGroupMember')
    assemblies = models.ManyToManyField('Assembly', through='Genome')
    organism_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    strain_type = models.CharField(max_length=128, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)

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
        ordering = ['biosample_id', 'scientific_name']


    @property
    def ensembl_name(self):
        return self.biosample_id

    @ensembl_name.setter
    def ensembl_name(self, ensembl_name):
        self.biosample_id = ensembl_name

    def __str__(self):
        return f"{self.scientific_name} ({self.biosample_id})"


class OrganismGroup(models.Model):
    class OrganismGroupType(models.TextChoices):
        DIVISION = 'Division', 'Ensembl GB Division'
        INTERNAL = 'Internal', 'Internal Grouping'
        POPULATION = 'Population', 'Organisms population'
        SPECIES = 'Species', 'Organisms species'
        COMPARA = 'Compara', 'Organisms Comparative Genomics group'
    organism_group_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=32, choices=OrganismGroupType.choices, null=True, blank=False)
    name = models.CharField(max_length=255)
    code = models.CharField(unique=True, max_length=48, blank=True, null=True)

    class Meta:
        db_table = 'organism_group'
        unique_together = (('type', 'name'),)

    def __str__(self):
        return "Type:" + self.type + " Name:" + self.name


class OrganismGroupMember(models.Model):
    organism_group_member_id = models.AutoField(primary_key=True)
    is_reference = models.BooleanField(null=True)
    order = models.IntegerField(null=True, unique=False)
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE)
    organism_group = models.ForeignKey(OrganismGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'organism_group_member'
        unique_together = (('organism', 'organism_group'),)

    def __str__(self):
        return str(self.organism_group_member_id)
