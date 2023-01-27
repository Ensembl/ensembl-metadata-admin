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


class AssemblySequenceInline(admin.StackedInline):
    model = AssemblySequence
    fields = ['name', 'length']
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    read_only_fields = ('created',)
    fields = ['accession', 'name', 'ucsc_name', 'accession_body', 'level', 'assembly_default']
    list_filter = ('accession',)
    search_fields = ('accession',)
    order = ('accession',)
    inlines = (AssemblySequenceInline,)

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            read_only_fields += ('name',)
        return read_only_fields


#####RELEASE ADMIN PAGE#####

class GenomeReleaseInLine(admin.TabularInline):
    model = GenomeRelease
    fields = ['Assemblies', 'Organisms', 'Datasets']
    readonly_fields = ["Assemblies", 'Organisms', 'Datasets']
    can_delete = False
    can_update = False

    def Assemblies(self, obj):
        url_view = reverse('admin:ensembl_metadata_assembly_change',
                           args=(obj.genome.assembly.assembly_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.assembly.accession + "</a>")

    def Organisms(self, obj):
        # return obj.genome.organism.ensembl_name
        url_view = reverse('admin:ensembl_metadata_organism_change',
                           args=(obj.genome.organism.organism_id,))
        return mark_safe(u"<a href='" + url_view + "'>" + obj.genome.organism.ensembl_name + "</a>")

    def Datasets(self, obj):
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


class ReleaseAdmin(admin.ModelAdmin):
    read_only_fields = ('version', 'release_date', 'site', 'release_type', 'is_current', 'assemblies')
    search_fields = ('version',)
    list_display = ('version', 'release_date', 'site', 'release_type', 'is_current', 'assemblies')
    order = ('is_current', 'release_date',)
    inlines = (GenomeReleaseInLine,)

    def assemblies(self, obj):
        output = ''
        for genome in obj.genomes.all():
            output += str(genome.assembly) + ':' + str(genome.organism) + ', '
        return output

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
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


class OrganismAdmin(admin.ModelAdmin):
    # assemblies
    list_display = (
        'display_name', 'Releases', 'Assembly_List', 'strain', 'scientific_name', 'ensembl_name',
        'scientific_parlance_name',
        'url_name', 'display_name', 'taxonomy_id', 'species_taxonomy_id',)
    list_filter = (MetadataReleaseFilter,)
    search_fields = ('ensembl_name', 'assemblies__accession')
    order = ('')
    inlines = (OrganismGroupMemberInLine, GenomeInLine)

    def Assembly_List(self, obj):
        return ",".join([str(p) for p in obj.assemblies.all()])

    def Releases(self, obj):
        genomes = EnsemblRelease.objects.all().filter(genomes__organism=obj).distinct()
        output = ''
        for i in genomes:
            output += str(i.version) + ", "
        return output

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            read_only_fields += ('scientific_parlance_name',)
        return read_only_fields


admin.site.register(Organism, OrganismAdmin)


#####Dataset ADMIN PAGE#####
class DatasetAttributeInline(admin.StackedInline):
    model = DatasetAttribute
    fields = ['type', 'value', 'attribute']
    # sortable_field_name = 'type'
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class DatasetAdmin(admin.ModelAdmin):
    read_only_fields = ('name', 'version', 'created', 'dataset_source', 'label')
    search_fields = ('name', 'dataset_source',)
    list_display = ('name', 'version', 'created', 'dataset_source', 'label')
    order = ('ensembl_name')
    list_filter = (MetadataReleaseFilter, 'dataset_type', MetadataOrganismFilter,)
    inlines = (DatasetAttributeInline,)


admin.site.register(Dataset, DatasetAdmin)


class OrganismGroupInLine(admin.StackedInline):
    model = OrganismGroupMember
    fields = ('is_reference', 'Organisms')
    readonly_fields = ("is_reference", 'Organisms',)
    can_delete = False
    can_update = False

    def Organisms(self, obj):
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
class OrganismGroupAdmin(admin.ModelAdmin):
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


class AttributeAdmin(admin.ModelAdmin):
    search_fields = ('ensembl_name', 'species_taxonomy_id',)
    list_display = ('name', 'label', 'description')
    order = ('name')


admin.site.register(Attribute, AttributeAdmin)
