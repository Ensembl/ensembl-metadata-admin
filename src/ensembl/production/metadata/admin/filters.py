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

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ensembl.production.metadata.admin.models import *


class MetadataReleaseFilter(admin.SimpleListFilter):
    title = _('Ensembl Release')
    parameter_name = 'ensembl_release'

    def lookups(self, request, model_admin):
        releases = EnsemblRelease.objects.all()
        return [(r.release_id, r.version) for r in releases] + [('-', '-')]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '-':
                return queryset.exclude(genome__releases__isnull=False)
            ensembl_release = EnsemblRelease.objects.get(pk=self.value())
            queryset = queryset.filter(genome__releases=ensembl_release)
            return queryset


class MetadataDatasetReleaseFilter(MetadataReleaseFilter):
    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '-':
                return queryset.exclude(genome_datasets__release__isnull=False)
            ensembl_release = EnsemblRelease.objects.get(pk=self.value())
            queryset = queryset.filter(genome_datasets__release=ensembl_release)
            return queryset


class MetadataOrganismFilter(admin.SimpleListFilter):
    title = _('Organism')
    parameter_name = 'organism'

    def lookups(self, request, model_admin):
        organisms = Organism.objects.all()
        return [(r.organism_id, r.biosample_id) for r in organisms]

    def queryset(self, request, queryset):
        if self.value():
            organism = Organism.objects.get(pk=self.value())
            return queryset.filter(genome__organism=organism)


class DatasetTypeListFilter(admin.SimpleListFilter):
    title = _("Dataset Type")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "dataset_type"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if request.user.is_superuser:
            types = DatasetType.objects.all()
        else:
            types = DatasetType.objects.filter(parent__isnull=True)

        return [(t.dataset_type_id, f"{t.label} ({t.name})") for t in types]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            dataset_type = DatasetType.objects.get(pk=self.value())
            return queryset.filter(dataset_type=dataset_type)
