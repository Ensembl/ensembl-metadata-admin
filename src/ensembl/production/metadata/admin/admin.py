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
from django.contrib.admin.options import InlineModelAdmin
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from ensembl.production.metadata.admin.filters import *
from .models import Attribute, AssemblySequence, Assembly, EnsemblRelease, Organism, Dataset, OrganismGroup, Genome, \
    DatasetAttribute
from django.utils.html import format_html, format_html_join
from django.contrib import admin, messages


def display_genome_uuid(obj):
    url = reverse('admin:ensembl_metadata_genome_change', args=[obj.pk])
    return format_html("<a href='{}'>{}</a>", url, obj.genome_uuid)


# Class to allow access only to turn everything readonly
class AdminMetadata(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return request.user.is_superuser or super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or super().has_add_permission(request)


class MetadataInline(InlineModelAdmin):
    can_delete = False
    can_update = False
    extra = 0

    def has_view_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.fields
        return super().get_readonly_fields(request, obj)


class GenomeInLine(MetadataInline, admin.TabularInline):
    model = Genome
    fields = ['display_genome_uuid', 'organism', 'production_name', 'is_best']  # Specify the fields to display
    readonly_fields = ['display_genome_uuid']
    can_delete = False
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def display_genome_uuid(self, obj):
        return display_genome_uuid(obj)

    display_genome_uuid.short_description = 'Genome UUID'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.title = None  # Remove the title
        return formset


class DAttributeInLine(MetadataInline, admin.TabularInline):
    # TODO We might nee to remove some linking, too many request generated. Page already takes around 1s to load with
    #  only 241 genomes
    model = DatasetAttribute
    fields = ['display_dataset_uuid', 'display_dataset_source_name', 'value']  # Updated fields list
    readonly_fields = ['display_dataset_uuid', 'display_dataset_source_name']  # Updated readonly fields
    can_delete = False
    extra = 0

    def display_dataset_uuid(self, obj):
        url = reverse('admin:ensembl_metadata_dataset_change', args=[obj.dataset.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.dataset.dataset_uuid)

    display_dataset_uuid.short_description = 'Dataset UUID'

    def display_dataset_source_name(self, obj):
        url = reverse('admin:ensembl_metadata_datasetsource_change', args=[obj.dataset.dataset_source.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.dataset.dataset_source.name)

    display_dataset_source_name.short_description = 'Dataset Source Name'

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Attribute)
class AttributeAdmin(AdminMetadata, admin.ModelAdmin):
    search_fields = ('name', 'type',)
    list_display = ('name', 'label', 'description', 'type')
    list_per_page = 30
    ordering = ('name',)
    inlines = (DAttributeInLine,)


@admin.register(AssemblySequence)
class AssemblySequenceAdmin(AdminMetadata, admin.ModelAdmin):
    model = AssemblySequence

    fields = ['name', 'assembly', 'accession', 'type', 'chromosomal', 'chromosome_rank', 'length', 'sequence_location',
              'is_circular', 'sha512t24u', 'md5', ]
    readonly_fields = fields  # ALL READONLY
    list_display = ['name', 'accession', 'length', 'chromosomal', 'md5', 'sha512t24u']
    search_fields = ['name', 'accession', 'md5', 'sha512t24u']
    list_per_page = 30
    object_id = None

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.object_id = object_id
        return super().change_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        if not (request.GET.get('assembly__assembly_id__exact') or self.object_id):
            messages.warning(request, "Please Filter per Assembly first.")
            return AssemblySequence.objects.none()
        else:
            return super().get_queryset(request)


@admin.register(Assembly)
class AssemblyAdmin(AdminMetadata, admin.ModelAdmin):
    readonly_fields = ['name', 'accession', 'created', 'assembly_uuid', 'assembly_sequence', 'tol_id', 'level',
                       'alt_accession', 'ucsc_name']
    search_fields = ('accession', 'assembly_uuid', 'name')
    ordering = ('accession',)
    list_display = ['accession', 'assembly_uuid', 'name', 'ucsc_name', 'level', 'assembly_sequence', 'alt_accession',
                    'is_reference']
    fieldsets = (
        (None, {
            'fields': ('name', 'assembly_uuid', 'accession', 'alt_accession', 'ucsc_name', 'tol_id', 'level')
        }),
        ('Details', {
            'fields': ('created', 'is_reference', 'assembly_sequence',
                       'assembly_default', 'accession_body', 'url_name'),
        })
    )
    list_filter = ('level', 'is_reference')
    inlines = (GenomeInLine,)

    def assembly_sequence(self, obj):
        url_view = reverse('admin:ensembl_metadata_assemblysequence_changelist')
        return mark_safe(
            f"<a href='{url_view}?assembly__assembly_id__exact={obj.assembly_id}'>View Assembly sequences</a>")

    assembly_sequence.short_description = "Sequences"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('name',)
        return readonly_fields


# #####RELEASE ADMIN PAGE#####
class GenomeReleaseInLine(MetadataInline, admin.TabularInline):
    model = GenomeRelease
    verbose_name = 'Genome in Release'
    verbose_name_plural = 'Genomes in Release'
    fields = ['genome_genome', 'genome_assembly', 'genome_organism', 'is_current']
    readonly_fields = ['genome_genome', 'genome_assembly', 'genome_organism', 'is_current']
    can_delete = False
    can_update = False
    extra = 0
    ordering = ['genome__genome_uuid']

    def has_add_permission(self, request, obj):
        return False

    def genome_genome(self, obj):
        return display_genome_uuid(obj.genome)

    genome_genome.short_description = "Genome"

    def genome_assembly(self, obj):
        url_view = reverse('admin:ensembl_metadata_assembly_change',
                           args=(obj.genome.assembly.assembly_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.assembly.accession + "</a>")

    genome_assembly.short_description = "Assembly"

    def genome_organism(self, obj):
        # return obj.genome.organism.biosample_id
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.genome.organism.organism_id,))
        return mark_safe(f"<a href='{url_view}'>{obj.genome.organism.display_name}</a>")

    genome_organism.short_description = "Organism"


class ReleaseDatasetInline(MetadataInline, admin.TabularInline):
    model = GenomeDataset
    verbose_name = 'Dataset in Release'
    verbose_name_plural = 'Datasets in Release'
    fields = ['dataset_uuid', 'genome_uuid', 'dataset_topic', 'dataset_status']
    readonly_fields = ['dataset_uuid', 'genome_uuid', 'dataset_topic', 'dataset_status']
    can_delete = False
    can_update = False
    extra = 0
    ordering = ['genome__genome_uuid', 'dataset__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(dataset__parent__isnull=True)
        qs = qs.prefetch_related('dataset', 'genome', 'dataset__dataset_type')
        return qs

    def has_add_permission(self, request, obj):
        return False

    def dataset_uuid(self, obj):
        url = reverse('admin:ensembl_metadata_dataset_change', args=[obj.dataset.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.dataset.dataset_uuid)

    dataset_uuid.short_description = "Dataset uuid"

    def genome_uuid(self, obj):
        return display_genome_uuid(obj.genome)

    genome_uuid.short_description = "Genome uuid"

    def dataset_topic(self, obj):
        return obj.dataset.dataset_type.topic

    dataset_topic.short_description = "Dataset topic"

    def dataset_status(self, obj):
        return obj.dataset.status

    dataset_status.short_description = "Dataset status"


@admin.register(EnsemblRelease)
class ReleaseAdmin(AdminMetadata, admin.ModelAdmin):
    # TODO add message for inconsistency detected in metadata release
    fields = ('get_status_display', 'release_date', 'release_type', 'is_current', 'label')
    readonly_fields = ('get_status_display', 'release_date', 'site', 'release_type', 'is_current')
    search_fields = ('version',)
    list_filter = ('is_current', 'release_type', 'site')
    list_display = ('version', 'release_date', 'label', 'release_type', 'is_current', 'get_status_display')
    inlines = (GenomeReleaseInLine, ReleaseDatasetInline)

    def get_status_display(self, obj):
        return obj.status

    get_status_display.short_description = "Release status"

    def genome_assembly(self, obj):
        output = ''
        for genome in obj.genomes.all():
            output += str(genome.assembly) + ':' + str(genome.organism) + ', '
        return output

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('version', 'label')
        return readonly_fields


# #####ORGANISM ADMIN PAGE#####

class OrganismGroupMemberInLine(MetadataInline, admin.TabularInline):
    model = OrganismGroupMember
    verbose_name = "Organisms Group"
    verbose_name_plural = "Organisms Groups"
    fields = ['display_organism_group_name', 'display_organism_group_type', 'is_reference']  # Updated fields list
    readonly_fields = ['display_organism_group_name', 'display_organism_group_type']  # Updated readonly fields
    can_delete = False
    can_update = False

    def display_organism_group_name(self, obj):
        url = reverse('admin:ensembl_metadata_organismgroup_change', args=[obj.organism_group.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.organism_group.name)

    display_organism_group_name.short_description = 'Group Name'

    def display_organism_group_type(self, obj):
        return obj.organism_group.type

    display_organism_group_type.short_description = 'Group Type'


@admin.register(Organism)
class OrganismAdmin(AdminMetadata, admin.ModelAdmin):
    # assemblies
    # TODO: integrate Releases / Assemblies in detailed view as Inlines
    fields = (
        'common_name', 'organism_uuid', 'strain', 'scientific_name', 'biosample_id',
        'scientific_parlance_name', 'taxonomy_id', 'species_taxonomy_id',)
    list_display = ('organism_uuid',
                    'common_name', 'strain', 'scientific_name', 'biosample_id',
                    'scientific_parlance_name', 'taxonomy_id', 'species_taxonomy_id')
    readonly_fields = ('organism_uuid', 'biosample_id', 'scientific_parlance_name')
    list_filter = (MetadataReleaseFilter,)
    search_fields = ('biosample_id', 'assemblies__accession', 'organism_uuid', 'common_name')
    inlines = (OrganismGroupMemberInLine, GenomeInLine)

    def organism_assemblies(self, obj):
        links = format_html_join(
            ', ',
            "<a href='{}'>{}</a>",
            ((reverse('admin:ensembl_metadata_assembly_change', args=[assembly.pk]), assembly) for assembly in
             obj.assemblies.all())
        )
        return links or '-'

    organism_assemblies.short_description = 'Assemblies'

    def genome_releases(self, obj):
        genomes = EnsemblRelease.objects.all().filter(genomes__organism=obj).distinct()
        links = format_html_join(
            ', ',
            "<a href='{}'>{}</a>",
            ((reverse('admin:ensembl_metadata_ensemblrelease_change', args=[genome.pk]), genome.version) for genome in
             genomes)
        )
        return links or '-'

    genome_releases.short_description = 'Releases'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('scientific_parlance_name',)
        return readonly_fields


# #####Dataset ADMIN PAGE#####
class DatasetAttributeInline(MetadataInline, admin.TabularInline):
    model = DatasetAttribute
    fields = ['attribute', 'value']
    ordering = ['attribute']
    filter = ''

    def has_change_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) or request.user.is_superuser

    def has_add_permission(self, request, obj):
        return request.user.is_superuser

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'attribute':
            return super().get_field_queryset(db, db_field, request).filter(name__startswith=self.filter)
        else:
            return super().get_field_queryset(db, db_field, request)

    def get_formset(self, request, obj=None, **kwargs):
        if obj is not None:
            type_name = obj.dataset_type.name
            if type_name in ('assembly', 'genebuild'):
                self.filter = type_name
            elif type_name in ('regulation_build', 'regulatory_features'):
                self.filter = 'regulation'
            elif type_name in ('variation', 'evidence'):
                self.filter = 'variation'
            elif type_name == 'homologies':
                self.filter = 'compara'
            else:
                self.filter = 'dataset'
        return super(DatasetAttributeInline, self).get_formset(request, obj, **kwargs)


class DatasetGenomeInline(MetadataInline, admin.TabularInline):
    model = GenomeDataset
    fields = ['genome_uuid', 'release_version', 'is_current']
    readonly_fields = ['genome_uuid', 'release_version']
    extra = 0
    can_update = False
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def genome_uuid(self, obj):
        return display_genome_uuid(obj.genome)


@admin.register(Dataset)
class DatasetAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'version', 'dataset_type', 'dataset_source', 'label', 'status_display')
    search_fields = ('dataset_uuid', 'genomes__genome_uuid', 'genomes__organism__common_name',
                     'genomes__organism__biosample_id', 'genomes__organism__scientific_name',
                     'genomes__assembly__accession', 'genomes__assembly__name',
                     'genomes__assembly__tol_id', 'genomes__assembly__ensembl_name')
    list_display = ('dataset_uuid', 'name', 'label', 'version', 'status_display', 'dataset_type')
    # ordering = ('-ensemblrelease__version', 'genomes__organism__name',)
    list_filter = (MetadataDatasetReleaseFilter, DatasetTypeListFilter, 'dataset_type__topic', 'status')
    inlines = (DatasetGenomeInline, DatasetAttributeInline)
    readonly_fields = ('status_display', 'dataset_type', 'dataset_source')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(parent__isnull=True)
        qs = qs.prefetch_related('genomes__organism', 'genomes__assembly', 'genomes__releases')
        return qs

    def status_display(self, obj):
        return obj.get_status_display()

    status_display.short_description = "Status"

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('created',)


#
class OrganismGroupInLine(MetadataInline, admin.TabularInline):
    model = OrganismGroupMember
    fields = ('group_organisms', 'is_reference')
    readonly_fields = ('group_organisms',)
    can_delete = False
    ordering = ('organism__scientific_name',)

    def group_organisms(self, obj):
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.organism.organism_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + str(obj.organism) + "</a>")

    def is_reference(self, obj):
        return obj.is_reference

    group_organisms.short_description = 'Organisms'
    is_reference.short_description = 'Is Reference for group'


# # Groups Admin Section
@admin.register(OrganismGroup)
class OrganismGroupAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'type', 'code')
    list_display = ('name', 'type', 'code')
    list_filter = ('name',)
    inlines = (OrganismGroupInLine,)


class GenomeDatasetInline(MetadataInline, admin.TabularInline):
    model = Genome.datasets.through
    fields = ['display_dataset', 'name', 'type', 'release_version', 'is_current', 'dataset_topic',
              'status_display']  # Updated fields list
    readonly_fields = ['display_dataset', 'name', 'type', 'release_version', 'is_current',
                       'status_display', 'dataset_topic']  # Updated readonly fields
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def display_dataset(self, obj):
        url = reverse('admin:ensembl_metadata_dataset_change', args=[obj.dataset.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.dataset.dataset_uuid)

    def status_display(self, obj):
        return obj.dataset.get_status_display()

    def dataset_topic(self, obj):
        return obj.dataset.dataset_type.topic

    display_dataset.short_description = 'Dataset'
    status_display.short_description = 'Status'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(dataset__parent__isnull=True)
        return queryset


class GenomeReleaseInline(MetadataInline, admin.TabularInline):
    model = Genome.releases.through
    fields = ['release_info', 'is_current', 'release__release_date']
    readonly_fields = ['release_info', 'is_current', 'release__release_date']

    def has_add_permission(self, request, obj):
        return super().has_add_permission(request, obj) or request.user.is_superuser

    def release__release_date(self, obj):
        return obj.release.release_date


@admin.register(Genome)
class GenomeAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ['genome_uuid', 'assembly', 'organism', 'is_best']
    list_filter = ['releases', 'is_best']
    # TODO add an item to list with NULL value
    search_fields = ['assembly__name', 'organism__common_name', 'genome_uuid']
    fields = ['genome_uuid', 'assembly', 'organism', 'production_name', 'is_best', 'created']
    readonly_fields = ['production_name', 'genome_uuid', 'assembly', 'organism', 'created']
    inlines = [GenomeDatasetInline, GenomeReleaseInline]


class DatasetInline(MetadataInline, admin.TabularInline):
    model = Dataset
    fields = ('dataset_uuid', 'name', 'version', 'label', 'status', 'created')
    readonly_fields = ('dataset_uuid', 'name', 'version', 'label', 'status', 'created')
    ordering = ('-created',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(DatasetSource)
class SourceAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ['name', 'type']
    search_fields = ['type', 'name']
    list_filter = ['type']
    inlines = [DatasetInline]


class SubDatasetTypeInline(MetadataInline, admin.TabularInline):
    model = DatasetType
    fields = ('name', 'label', 'topic', 'description')


class AdminTypeForm(forms.ModelForm):
    TOPIC_CHOICES = (
        ('assembly', 'Assembly'),
        ('genebuild_annotation', 'Genebuild Annotation'),
        ('compara_annotation', 'Compara Annotation'),
        ('regulation_annotation', 'Regulation Annotation'),
        ('variation_annotation', 'Variation Annotation'),
        ('production_process', 'Production Processing'),
        ('production_preparation', 'Production Preparation'),
        ('production_publication', 'Production Publication')
    )
    topic = forms.ChoiceField(choices=TOPIC_CHOICES)


@admin.register(DatasetType)
class TypeAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'label', 'topic', 'description', 'parent')
    readonly_fields = ['name']
    list_display = ['name', 'label', 'topic', 'description']
    list_filter = ['topic']
    inlines = [SubDatasetTypeInline]
    ordering = ['name']
    form = AdminTypeForm

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EnsemblSite)
class SiteAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ['name', 'label', 'display_uri']
    search_fields = ['name', 'label', 'uri']

    def display_uri(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.uri)

    display_uri.short_description = 'URI'
    display_uri.admin_order_field = 'uri'  # Allows column sorting based on the 'uri' field
