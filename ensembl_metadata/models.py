# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib import admin


class Assembly(models.Model):
    assembly_id = models.AutoField(primary_key=True)
    ucsc_name = models.CharField(max_length=16, blank=True, null=True)
    accession = models.CharField(unique=True, max_length=16)
    level = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    accession_body = models.CharField(max_length=32, blank=True, null=True)
    assembly_default = models.CharField(max_length=32, blank=True, null=True)
    tolid = models.CharField(unique=True, max_length=32, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    ensembl_name = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'assembly'
        verbose_name_plural = 'Assemblies'

    def __str__(self):
        return self.name


class AssemblySequence(models.Model):
    assembly_sequence_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)
    accession = models.CharField(max_length=32)
    chromosomal = models.IntegerField()
    length = models.IntegerField()
    sequence_location = models.CharField(max_length=10, blank=True, null=True)
    sequence_checksum = models.CharField(max_length=32, blank=True, null=True)
    ga4gh_identifier = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'assembly_sequence'
        unique_together = (('assembly', 'accession'),)
    def __str__(self):
        return self.name

class Attribute(models.Model):
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    label = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'attribute'
    def __str__(self):
        return self.name

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Dataset(models.Model):
    dataset_id = models.AutoField(primary_key=True)
    dataset_uuid = models.CharField(unique=True, max_length=128)
    dataset_type = models.ForeignKey('DatasetType', models.DO_NOTHING)
    name = models.CharField(max_length=128)
    version = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField()
    dataset_source = models.ForeignKey('DatasetSource', models.DO_NOTHING)
    label = models.CharField(max_length=128)

    class Meta:
        db_table = 'dataset'
    def __str__(self):
        return self.name

class DatasetAttribute(models.Model):
    dataset_attribute_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=32)
    value = models.CharField(max_length=128)
    attribute = models.ForeignKey(Attribute, models.DO_NOTHING)
    dataset = models.ForeignKey(Dataset, models.DO_NOTHING)

    class Meta:
        db_table = 'dataset_attribute'
        unique_together = (('dataset', 'attribute', 'type', 'value'),)
    def __str__(self):
        return self.type

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

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EnsemblRelease(models.Model):
    release_id = models.AutoField(primary_key=True)
    version = models.DecimalField(max_digits=10, decimal_places=1)
    release_date = models.DateField()
    label = models.CharField(max_length=64, blank=True, null=True)
    is_current = models.BooleanField()
    site = models.ForeignKey('EnsemblSite', models.DO_NOTHING, blank=True, null=True)
    release_type = models.CharField(max_length=16)
    genomes = models.ManyToManyField('Genome',through='GenomeRelease')

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
    genome_uuid = models.CharField(unique=True, max_length=128)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)
    organism = models.ForeignKey('Organism', models.DO_NOTHING)
    created = models.DateTimeField()

    class Meta:
        db_table = 'genome'
    def __str__(self):
        return self.genome_uuid

class GenomeDataset(models.Model):
    genome_dataset_id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, models.DO_NOTHING)
    genome = models.ForeignKey(Genome, models.DO_NOTHING)
    release = models.ForeignKey(EnsemblRelease, models.DO_NOTHING)
    is_current = models.IntegerField()

    class Meta:
        db_table = 'genome_dataset'


class GenomeRelease(models.Model):
    genome_release_id = models.AutoField(primary_key=True)
    genome = models.ForeignKey(Genome, models.DO_NOTHING)
    release = models.ForeignKey(EnsemblRelease, models.DO_NOTHING)
    is_current = models.IntegerField()


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
    groups = models.ManyToManyField('OrganismGroup',through='OrganismGroupMember')
    assemblies = models.ManyToManyField('Assembly',through='Genome')


    def assembly_list(self):
        return ",".join([str(p) for p in self.assemblies.all()])

    # genome_releases = models.ManyToManyField('GenomeRelease', through='Genome')
    # def release_list(self):
    #     output = '';
    #     for genome in self.genome_releases.all():
    #         release = 'link out to the release here'
    #         output += release
    #
    #     return output
    #     return ",".join([str(p) for p in self.genome_releases.all()])
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
        return "Type:"+self.type+" Name:"+self.name

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