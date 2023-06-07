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


from django.urls import reverse
from django.utils.safestring import mark_safe

from ensembl.production.metadata.admin.filters import *


# Temporary class to allow access only to turn everything readonly
class AdminMetadata(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class AssemblySequenceInline(admin.TabularInline):
    model = AssemblySequence
    fields = ['name', 'length']
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Assembly)
class AssemblyAdmin(AdminMetadata, admin.ModelAdmin):
    read_only_fields = ('created',)
    fields = ['accession', 'name', 'ucsc_name', 'accession_body', 'level', 'assembly_default']
    list_filter = ('accession',)
    search_fields = ('accession',)
    order = ('accession',)
    inlines = (AssemblySequenceInline,)

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            read_only_fields += ('name',)
        return read_only_fields


#####RELEASE ADMIN PAGE#####

class GenomeReleaseInLine(admin.TabularInline):
    model = GenomeRelease
    fields = ['genome_assembly', 'genome_organism', 'genome_datasets']
    readonly_fields = ['genome_assembly', 'genome_organism', 'genome_datasets']
    can_delete = False
    can_update = False

    def genome_assembly(self, obj):
        url_view = reverse('admin:ensembl_metadata_assembly_change',
                           args=(obj.genome.assembly.assembly_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.assembly.accession + "</a>")

    def genome_organism(self, obj):
        # return obj.genome.organism.ensembl_name
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.genome.organism.organism_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.organism.ensembl_name + "</a>")

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

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReleaseAdmin(AdminMetadata, admin.ModelAdmin):
    read_only_fields = ('version', 'release_date', 'site', 'release_type', 'is_current')
    search_fields = ('version',)
    list_display = ('version', 'release_date', 'site', 'release_type', 'is_current')
    order = ('is_current', 'release_date',)
    inlines = (GenomeReleaseInLine,)

    def genome_assembly(self, obj):
        output = ''
        for genome in obj.genomes.all():
            output += str(genome.assembly) + ':' + str(genome.organism) + ', '
        return output

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            read_only_fields += ('version',)
        return read_only_fields


admin.site.register(EnsemblRelease, ReleaseAdmin)


#####ORGANISM ADMIN PAGE#####
class GenomeInLine(admin.TabularInline):
    model = Genome
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrganismGroupMemberInLine(admin.StackedInline):
    model = OrganismGroupMember
    fields = ['is_reference', 'organism_group']
    # readonly_fields = ["is_reference", 'Type', 'Label', 'Group_Code']
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrganismAdmin(AdminMetadata, admin.ModelAdmin):
    # assemblies
    list_display = (
        'display_name', 'genome_releases', 'organism_assemblies', 'strain', 'scientific_name', 'ensembl_name',
        'scientific_parlance_name',
        'url_name', 'display_name', 'taxonomy_id', 'species_taxonomy_id',)
    list_filter = (MetadataReleaseFilter,)
    search_fields = ('ensembl_name', 'assemblies__accession')
    order = ('')
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
        read_only_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            read_only_fields += ('scientific_parlance_name',)
        return read_only_fields


admin.site.register(Organism, OrganismAdmin)


#####Dataset ADMIN PAGE#####
class DatasetAttributeInline(admin.StackedInline):
    model = DatasetAttribute
    fields = ['value', 'attribute']
    can_delete = False
    can_update = False


class DatasetAdmin(AdminMetadata, admin.ModelAdmin):
    fields = ('name', 'version', 'dataset_type', 'created', 'dataset_source', 'label', 'status')
    search_fields = ('genomes__genome_uuid', 'genomes__organism__display_name',
                     'genomes__organism__ensembl_name', 'genomes__organism__scientific_name',
                     'genomes__assembly__accession', 'genomes__assembly__name',
                     'genomes__assembly__tol_id', 'genomes__assembly__ensembl_name')
    list_display = ('name', 'label', 'version',)
    ordering = ('-genomes__releases__version', 'genomes__organism__name')
    list_filter = (MetadataOrganismFilter,)
    inlines = (DatasetAttributeInline,)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('genomes__organism', 'genomes__assembly', 'genomes__releases')


admin.site.register(Dataset, DatasetAdmin)


class OrganismGroupInLine(admin.StackedInline):
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

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Groups Admin Section
class OrganismGroupAdmin(AdminMetadata, admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.none()
        return qs

    fields = ('name', 'type', 'code')
    list_display = ('type', 'name', 'code')

    list_filter = ('name',)

    inlines = (OrganismGroupInLine,)


admin.site.register(OrganismGroup, OrganismGroupAdmin)


class AttributeAdmin(AdminMetadata, admin.ModelAdmin):
    list_display = ('name', 'label', 'description', 'type')
    order = ('name')


admin.site.register(Attribute, AttributeAdmin)
