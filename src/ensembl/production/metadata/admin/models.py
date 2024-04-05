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
#   limitations under the License.
import uuid

import jsonfield.fields
from django.core.exceptions import ValidationError
from django.db import models


class UUIDField(models.UUIDField):

    def __init__(self, verbose_name=None, **kwargs):
        kwargs['max_length'] = 36
        # jump over first parent hierarchy
        super(models.UUIDField, self).__init__(verbose_name, **kwargs)


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
    assembly_uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    type = models.CharField(choices=SequenceType.choices, max_length=26, blank=True, null=False,
                            default=SequenceType.PRIMARY)
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


class DatasetManager(models.Manager):
    def create_child_datasets(self, instance, genome):
        # FYI Needs to be correlated with SQLAlchemy counter part:
        # https://github.com/Ensembl/ensembl-metadata-api/blob/main/src/ensembl/production/metadata/api/factories/datasets.py#L26
        kids_type = DatasetType.objects.filter(parent=instance.dataset_type)
        for kid in kids_type.all():
            ds = self.create(dataset_type=kid,
                             label=f"{kid.name} from {instance.dataset_type.name}",
                             dataset_source=instance.dataset_source,
                             name=kid.name,
                             status=instance.status,
                             parent=instance)
            GenomeDataset.objects.create(genome=genome, dataset=ds)
            self.create_child_datasets(ds, genome)


class Dataset(models.Model):
    class DatasetStatus(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        PROCESSING = 'PROCESSING', 'Processing'
        PROCESSED = 'PROCESSED', 'Processed'
        RELEASED = 'RELEASED', 'Released'

    objects = DatasetManager()
    dataset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    version = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    dataset_source = models.ForeignKey('DatasetSource', on_delete=models.CASCADE)
    label = models.CharField(max_length=128)
    attributes = models.ManyToManyField('Attribute', through='DatasetAttribute', related_name='dataset_attributes')
    status = models.CharField(max_length=12, choices=DatasetStatus.choices, default=DatasetStatus.SUBMITTED)
    genomes = models.ManyToManyField('Genome', through='GenomeDataset')
    dataset_type = models.ForeignKey('DatasetType', models.DO_NOTHING)
    dataset_uuid = UUIDField(default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('Dataset', default=None, null=True, db_column='parent_id',
                               on_delete=models.CASCADE)

    class Meta:
        db_table = 'dataset'

    def save(self, *args, **kwargs):
        if self.pk and self.genomes.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be modified')
        else:
            created = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.genomes.filter(releases__isnull=False).exists():
            raise ValidationError('Released data cannot be deleted')
        super().delete(*args, **kwargs)

    def status_value(self):
        return f"{self.status}"

    def __str__(self):
        return f"{self.name}[{self.dataset_uuid}]"


class DatasetAttribute(models.Model):
    dataset_attribute_id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=128)
    attribute = models.ForeignKey('Attribute', on_delete=models.CASCADE, related_name='datasets_set')
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, related_name='attributes_set')

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
    parent = models.ForeignKey("DatasetType", db_column='parent_id', blank=True, null=True, on_delete=models.SET_NULL)
    depends_on = models.CharField(max_length=128, blank=True, null=True)
    filter_on = jsonfield.JSONField(blank=True, null=True)  # JSON field

    class Meta:
        db_table = 'dataset_type'
        ordering = ['label']

    def __str__(self):
        return self.name


class EnsemblRelease(models.Model):
    class ReleaseStatus(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        PREPARING = 'PREPARING', 'Preparing'
        PREPARED = 'PREPARED', 'Prepared'
        RELEASED = 'RELEASED', 'Released'

    release_id = models.AutoField(primary_key=True)
    version = models.DecimalField(max_digits=10, decimal_places=1)
    release_date = models.DateField(null=True, blank=True)
    label = models.CharField(max_length=64, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    site = models.ForeignKey('EnsemblSite', on_delete=models.SET_NULL, blank=True, null=True)
    release_type = models.CharField(max_length=16)
    genomes = models.ManyToManyField('Genome', through='GenomeRelease')
    datasets = models.ManyToManyField('Dataset', through='GenomeDataset')
    status = models.CharField(max_length=12, choices=ReleaseStatus.choices, default=ReleaseStatus.PLANNED)

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
    genebuild_version = models.CharField(max_length=64, null=True, unique=False)
    genebuild_date = models.CharField(max_length=20, null=True, unique=False)

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
    class Meta:
        db_table = 'genome_dataset'
        constraints = [
            models.UniqueConstraint(
                fields=['dataset', 'genome'], name='unique_dataset_genome'
            )
        ]

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

    @property
    def name(self):
        return self.dataset.name

    @property
    def type(self):
        return self.dataset.dataset_type.name if self.dataset.dataset_type else 'n/a'

    def release_version(self):
        print("Release!!!!", self.release)
        return self.release.version if self.release else 'Unreleased'


class GenomeRelease(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['release', 'genome'], name='unique_release_genome'
            )
        ]

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

    @property
    def release_version(self):
        return self.release.version

    @property
    def release_info(self):
        return f"{self.release.version} --- {self.release.label} ({self.release.site.name})"


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
    organism_uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
