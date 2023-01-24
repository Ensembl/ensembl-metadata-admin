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
from django.contrib import admin
from ensembl.production.metadata.admin.models import *


class AssemblySequenceInline(admin.StackedInline):
    model = AssemblySequence
    fields = ['name', 'length']
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AssemblyInLine(admin.StackedInline):
    model = Assembly
    fields = ['accession', 'name', 'ucsc_name', 'accession_body', 'level', 'assembly_default']
    can_delete = False
    can_update = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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


class OrganismGroupInLine(admin.TabularInline):
    model = OrganismGroup
    sortable_field_name = "name"
    fields = ['type', 'name', 'code']

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrganismGroupMemberInLine(admin.TabularInline):
    model = OrganismGroupMember

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class GenomeInLine(admin.TabularInline):
    model = Genome
    can_delete = False
    can_update = False
    # def has_add_permission(self, request, obj):
    #     return False
    # def has_change_permission(self, request, obj=None):
    #     return False


class GenomeReleaseInLine(admin.TabularInline):
    model = GenomeRelease
    can_delete = False
    can_update = False
    inlines = (GenomeInLine, AssemblyInLine)

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrganismInLine(admin.StackedInline):
    model = Organism
    fields = ['name']
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


@admin.register(EnsemblRelease)
class ReleaseAdmin(admin.ModelAdmin):
    read_only_fields = ('version', 'release_date', 'site', 'release_type', 'is_current')
    search_fields = ('version',)
    list_display = ('version', 'release_date', 'site', 'release_type', 'is_current')
    order = ('is_current', 'release_date',)
    inlines = (GenomeReleaseInLine,)

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            read_only_fields += ('version',)
        return read_only_fields


class OrganismAdmin(admin.ModelAdmin):
    read_only_fields = ('version', 'release_date', 'site', 'release_type', 'is_current')
    search_fields = ('ensembl_name', 'species_taxonomy_id',)
    list_display = (
        'display_name', 'strain', 'scientific_name', 'display_name', 'ensembl_name', 'scientific_parlance_name',
        'taxonomy_id', 'species_taxonomy_id', 'url_name', 'assembly_list')
    order = ('ensembl_name')
    inlines = (OrganismGroupMemberInLine, GenomeInLine)

    def get_readonly_fields(self, request, obj=None):
        read_only_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            read_only_fields += ('scientific_parlance_name',)
        return read_only_fields


admin.site.register(Organism, OrganismAdmin)


class OrganismGroupAdmin(admin.ModelAdmin):
    inlines = (OrganismGroupMemberInLine,)


admin.site.register(OrganismGroup, OrganismGroupAdmin)


class DatasetAdmin(admin.ModelAdmin):
    read_only_fields = ('name', 'version', 'created', 'dataset_source', 'label')
    search_fields = ('name', 'dataset_source',)
    list_display = ('name', 'version', 'created', 'dataset_source', 'label')
    order = ('ensembl_name')
    inlines = (DatasetAttributeInline,)


admin.site.register(Dataset, DatasetAdmin)


class AttributeAdmin(admin.ModelAdmin):
    search_fields = ('ensembl_name', 'species_taxonomy_id',)
    list_display = ('name', 'label', 'description')
    order = ('name')


admin.site.register(Attribute, AttributeAdmin)
