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
from django.contrib.admin.options import InlineModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from ensembl.production.metadata.admin.filters import *
from .models import Attribute, AssemblySequence, Assembly, EnsemblRelease, Organism, Dataset, OrganismGroup, Genome, DatasetAttribute
from django.utils.html import format_html, format_html_join


# Temporary class to allow access only to turn everything readonly
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


class GenomeInLine(MetadataInline, admin.TabularInline):
    model = Genome
    fields = ['display_genome_uuid', 'organism', 'production_name', 'is_best']  # Specify the fields to display
    readonly_fields = ['display_genome_uuid']   #Not editable field
    can_delete = False
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False
    def display_genome_uuid(self, obj):
        url = reverse('admin:ensembl_metadata_genome_change', args=[obj.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.genome_uuid)
    display_genome_uuid.short_description = 'Genome UUID'
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.title = None  # Remove the title
        return formset


class DAttributeInLine(MetadataInline, admin.TabularInline):
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

    fields = ['name', 'assembly', 'accession', 'chromosomal','chromosome_rank', 'length', 'sequence_location','sha512t24u', 'md5']
    readonly_fields = ['name', 'assembly', 'accession', 'sha512t24u', 'md5']
    list_display = ['name', 'accession', 'length','chromosomal']
    search_fields = ['assembly__accession','name', 'chromosomal', 'length']
    # NOTE: the list filter might grow a lot, we'd like to find a better way
    list_filter = ['assembly']
    # list_display_links = None
    list_per_page = 30

@admin.register(Assembly)
class AssemblyAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ['name', 'accession', 'assembly_uuid', 'ucsc_name', 'accession_body', 'level', 'assembly_default', 'assembly_sequence', 'alt_accession', 'is_reference', 'tol_id']
    readonly_fields = ['name', 'accession',  'created', 'assembly_uuid','assembly_sequence']
    search_fields = ('accession','assembly_uuid', 'name')
    ordering = ('accession',)
    list_display = ['accession', 'assembly_uuid', 'name', 'ucsc_name', 'level', 'assembly_sequence', 'alt_accession', 'is_reference']
    list_filter = ('level', 'is_reference')
    inlines = (GenomeInLine,)

    def assembly_sequence(self, obj):
        url_view = reverse('admin:ensembl_metadata_assemblysequence_changelist')
        return mark_safe(f"<a href='{url_view}?assembly__assembly_id__exact={obj.assembly_id}'>View</a>")
    assembly_sequence.short_description = "Sequences"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('name',)
        return readonly_fields


# #####RELEASE ADMIN PAGE#####
class GenomeReleaseInLine(MetadataInline, admin.TabularInline):
    model = GenomeRelease
    fields = ['genome_genome', 'genome_assembly', 'genome_organism', 'genome_datasets', 'is_current']
    readonly_fields = ['genome_genome', 'genome_assembly', 'genome_organism', 'genome_datasets', 'is_current']
    can_delete = False
    can_update = False
    extra = 0

    def genome_genome(self, obj):
        url_view = reverse('admin:ensembl_metadata_genome_change',
                           args=(obj.genome.genome_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + str(obj.genome.genome_uuid) + "</a>")

    genome_genome.short_description = "Genome"

    def genome_assembly(self, obj):
        url_view = reverse('admin:ensembl_metadata_assembly_change',
                           args=(obj.genome.assembly.assembly_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.assembly.accession + "</a>")

    genome_assembly.short_description = "Assembly"

    def genome_organism(self, obj):
        # return obj.genome.organism.ensembl_name
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.genome.organism.organism_id,))
        return mark_safe(f"<a href='{url_view}'>{obj.genome.organism.display_name}</a>")

    genome_organism.short_description = "Organism"

    def genome_datasets(self, obj):
        return ', '.join([d['dataset_type__name'] for d in obj.genome.datasets.values('dataset_type__name')])

    genome_datasets.short_description = "Datasets"


@admin.register(EnsemblRelease)
class ReleaseAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('release_date', 'site', 'release_type', 'is_current', 'label')
    readonly_fields = ('release_date', 'site', 'release_type', 'is_current')
    search_fields = ('version',)
    list_filter = ('is_current', 'release_type','site')
    list_display = ('version', 'release_date', 'label', 'site', 'release_type', 'is_current')
    ordering = ('-is_current', '-release_date',)
    inlines = (GenomeReleaseInLine,)

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
    fields = (
        'common_name', 'organism_uuid', 'strain', 'scientific_name', 'ensembl_name',
        'scientific_parlance_name', 'taxonomy_id', 'species_taxonomy_id',)
    list_display = (
        'common_name', 'genome_releases', 'organism_assemblies', 'strain', 'scientific_name', 'ensembl_name',
        'scientific_parlance_name', 'taxonomy_id', 'species_taxonomy_id', 'organism_uuid', )
    readonly_fields = ('organism_uuid', 'ensembl_name', 'scientific_parlance_name')
    list_filter = (MetadataReleaseFilter,)
    search_fields = ('ensembl_name', 'assemblies__accession', 'organism_uuid', 'common_name')
    inlines = (OrganismGroupMemberInLine, GenomeInLine)

    def organism_assemblies(self, obj):
        links = format_html_join(
            ', ',
            "<a href='{}'>{}</a>",
            ((reverse('admin:ensembl_metadata_assembly_change', args=[assembly.pk]), assembly) for assembly in obj.assemblies.all())
        )
        return links or '-'
    organism_assemblies.short_description = 'Assemblies'
    def genome_releases(self, obj):
        genomes = EnsemblRelease.objects.all().filter(genomes__organism=obj).distinct()
        links = format_html_join(
            ', ',
            "<a href='{}'>{}</a>",
            ((reverse('admin:ensembl_metadata_ensemblrelease_change', args=[genome.pk]), genome.version) for genome in genomes)
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
    can_delete = False
    can_update = False


@admin.register(Dataset)
class DatasetAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'version', 'dataset_type', 'dataset_source', 'label', 'status', 'dataset_uuid')
    search_fields = ('genomes__genome_uuid', 'genomes__organism__common_name',
                     'genomes__organism__ensembl_name', 'genomes__organism__scientific_name',
                     'genomes__assembly__accession', 'genomes__assembly__name',
                     'genomes__assembly__tol_id', 'genomes__assembly__ensembl_name')
    list_display = ('name', 'label', 'version', 'status_value', 'dataset_source', 'dataset_type', 'dataset_uuid')
    ordering = ('-genomes__releases__version', 'genomes__organism__name')
    list_filter = (MetadataReleaseFilter, 'dataset_type', 'status')
    inlines = (DatasetAttributeInline,)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('genomes__organism', 'genomes__assembly', 'genomes__releases')

    def status_display(self, obj):
        return obj.get_status_display()

    #
    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     if object_id:
    #         dataset = self.get_object(request, object_id)
    #         extra_context['status_display'] = dataset.get_status_display()
    #     return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('dataset_uuid', 'created',)


#
class OrganismGroupInLine(MetadataInline, admin.TabularInline):
    model = OrganismGroupMember
    fields = ('group_organisms', 'is_reference')
    readonly_fields = ('group_organisms',)
    can_delete = False

    def group_organisms(self, obj):
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.organism.organism_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.organism.ensembl_name + "</a>")
    group_organisms.short_description = 'Organisms'

#
#
# # Groups Admin Section
@admin.register(OrganismGroup)
class OrganismGroupAdmin(AdminMetadata, admin.ModelAdmin):

    fields = ('name', 'type', 'code')
    list_display = ('name', 'type', 'code')
    list_filter = ('name',)
    inlines = (OrganismGroupInLine,)


class GenomeDatasetInline(MetadataInline, admin.TabularInline):
    model = GenomeDataset
    fields = ['display_dataset', 'display_dataset_type_name', 'release', 'is_current']  # Updated fields list
    readonly_fields = ['display_dataset', 'display_dataset_type_name']  # Updated readonly fields
    can_delete = False
    extra = 0

    def display_dataset(self, obj):
        url = reverse('admin:ensembl_metadata_dataset_change', args=[obj.dataset.pk])
        return format_html("<a href='{}'>{}</a>", url, obj.dataset.dataset_uuid)
    display_dataset.short_description = 'Dataset'

    def display_dataset_type_name(self, obj):
        return obj.dataset.dataset_type.name if obj.dataset and obj.dataset.dataset_type else None
    display_dataset_type_name.short_description = 'Dataset Type'


@admin.register(Genome)
class GenomeAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ['genome_uuid', 'assembly', 'organism','is_best']
    list_filter = ['releases','is_best']
    search_fields = ['assembly', 'organism', 'genome_uuid']
    readonly_fields = ['genome_uuid', 'assembly', 'organism', 'created']
    inlines = [GenomeDatasetInline]


@admin.register(DatasetSource)
class SourceAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ['name', 'type']
    search_fields = ['type', 'name']
    list_filter = ['type']


@admin.register(DatasetType)
class TypeAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'label', 'topic', 'description', 'details_uri')
    readonly_fields = ['name']
    list_display = ['name', 'label', 'topic', 'description', 'details_uri']

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
