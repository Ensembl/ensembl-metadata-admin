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


# Temporary class to allow access only to turn everything readonly
class AdminMetadata(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


class MetadataInline(InlineModelAdmin):
    can_delete = False
    can_update = False
    extra = 0

    def has_view_permission(self, request, obj=None):
        return True


class GenomeInLine(MetadataInline, admin.TabularInline):
    model = Genome

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AssemblySequence)
class AssemblySequenceAdmin(AdminMetadata, admin.ModelAdmin):
    model = AssemblySequence
    fields = ['name', 'accession', 'length']
    list_display = ['name', 'accession', 'length']
    search_fields = ['assembly__accession']
    # NOTE: the list filter might grow a lot, we'd like to find a better way
    list_filter = ['assembly']
    list_display_links = None
    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Assembly)
class AssemblyAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ['accession', 'name', 'ucsc_name', 'accession_body', 'level', 'assembly_default', 'assembly_sequence']
    readonly_fields = ['accession', 'ucsc_name', 'accession_body', 'level', 'assembly_default', 'created',
                       'assembly_sequence']
    list_filter = ('accession',)
    search_fields = ('accession',)
    ordering = ('accession',)
    list_display = ['accession', 'name', 'ucsc_name', 'level', 'assembly_sequence']
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


#####RELEASE ADMIN PAGE#####
class GenomeReleaseInLine(MetadataInline, admin.TabularInline):
    model = GenomeRelease
    fields = ['genome_assembly', 'genome_organism', 'genome_datasets']
    readonly_fields = ['genome_assembly', 'genome_organism', 'genome_datasets']
    can_delete = False
    can_update = False
    extra = 0

    def genome_assembly(self, obj):
        url_view = reverse('admin:ensembl_metadata_assembly_change',
                           args=(obj.genome.assembly.assembly_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.assembly.accession + "</a>")

    def genome_organism(self, obj):
        # return obj.genome.organism.ensembl_name
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.genome.organism.organism_id,))
        return mark_safe(f"<a href='{url_view}'>{obj.genome.organism.display_name}</a>")

    def genome_datasets(self, obj):
        output = ''
        for i in obj.genome.datasets.all():
            output += i.name + ', '
        return output

        # output = []
        # for i in obj.genome.datasets.all():
        #     # output += i.name + ', '
        #     url_view = reverse('admin:ensembl_metadata_dataset_change',
        #                        args=(i.dataset_id,))
        #     output.append(mark_safe(u"<a href='" + url_view + "'>" + i.name + "</a>"))
        # return output


@admin.register(EnsemblRelease)
class ReleaseAdmin(AdminMetadata, admin.ModelAdmin):
    readonly_fields = ('release_date', 'site', 'release_type', 'is_current')
    search_fields = ('version',)
    list_display = ('version', 'release_date', 'site', 'release_type', 'is_current')
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


#####ORGANISM ADMIN PAGE#####


class OrganismGroupMemberInLine(MetadataInline, admin.StackedInline):
    model = OrganismGroupMember
    fields = ['is_reference', 'organism_group']
    # readonly_fields = ["is_reference", 'Type', 'Label', 'Group_Code']
    can_delete = False
    can_update = False


@admin.register(Organism)
class OrganismAdmin(AdminMetadata, admin.ModelAdmin):
    # assemblies
    list_display = (
        'display_name', 'genome_releases', 'organism_assemblies', 'strain', 'scientific_name', 'ensembl_name',
        'scientific_parlance_name',
        'url_name', 'display_name', 'taxonomy_id', 'species_taxonomy_id',)
    list_filter = (MetadataReleaseFilter,)
    search_fields = ('ensembl_name', 'assemblies__accession')
    inlines = (OrganismGroupMemberInLine, GenomeInLine)

    def organism_assemblies(self, obj):
        return ",".join([str(p) for p in obj.assemblies.all()])

    def genome_releases(self, obj):
        genomes = EnsemblRelease.objects.all().filter(genomes__organism=obj).distinct()
        output = ''
        for i in genomes:
            output += str(i.version) + ", "
        return output

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('scientific_parlance_name',)
        return readonly_fields


#####Dataset ADMIN PAGE#####
class DatasetAttributeInline(MetadataInline, admin.StackedInline):
    model = DatasetAttribute
    fields = ['value', 'attribute']
    can_delete = False
    can_update = False


@admin.register(Dataset)
class DatasetAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'version', 'dataset_type', 'created', 'dataset_source', 'label', 'status')
    search_fields = ('genomes__genome_uuid', 'genomes__organism__display_name',
                     'genomes__organism__ensembl_name', 'genomes__organism__scientific_name',
                     'genomes__assembly__accession', 'genomes__assembly__name',
                     'genomes__assembly__tol_id', 'genomes__assembly__ensembl_name')
    list_display = ('name', 'label', 'version')
    ordering = ('-genomes__releases__version', 'genomes__organism__name')
    list_filter = (MetadataReleaseFilter, 'dataset_type', MetadataOrganismFilter,)
    inlines = (DatasetAttributeInline,)

    def has_add_permission(self, request):
        return request.user.is_superuser or super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('genomes__organism', 'genomes__assembly', 'genomes__releases')


class OrganismGroupInLine(MetadataInline, admin.StackedInline):
    model = OrganismGroupMember
    fields = ('is_reference', 'group_organisms')
    readonly_fields = ("is_reference", 'group_organisms',)
    can_delete = False
    can_update = False

    def group_organisms(self, obj):
        # return obj.genome.organism.ensembl_name
        # return obj.organism
        # print (obj)
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.organism.organism_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.organism.ensembl_name + "</a>")


# Groups Admin Section
@admin.register(OrganismGroup)
class OrganismGroupAdmin(AdminMetadata, admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.none()
        return qs

    fields = ('name', 'type', 'code')
    list_display = ('name', 'type', 'code')
    list_filter = ('name',)
    inlines = (OrganismGroupInLine,)


@admin.register(Attribute)
class AttributeAdmin(AdminMetadata, admin.ModelAdmin):
    search_fields = ('ensembl_name', 'species_taxonomy_id',)
    list_display = ('name', 'label', 'description', 'type')
    list_per_page = 30
    ordering = ('name', )

    def has_add_permission(self, request):
        return request.user.is_superuser or super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser