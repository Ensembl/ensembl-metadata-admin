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

from rest_framework import serializers

from ensembl.production.metadata.admin.models import Genome, Assembly, Organism, Dataset, EnsemblRelease
from django.urls import reverse
class AssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = Assembly
        fields = ["accession"]
class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="ensembl_metadata:datasets-detail",lookup_field="dataset_uuid")
    class Meta:
        model = Dataset
        # fields = ['url', 'name']
        fields = ['name']
#        print(reverse('ensembl-metadata:api:datasets-detail', kwargs={'dataset_uuid': '559d7660-d92d-47e1-924e-e741151c2cef'}))

class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ["scientific_name", "ensembl_name"]

class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnsemblRelease
        fields = ["version"]

class GenomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genome
        fields = ["genome_uuid","created","releases","datasets", "assembly", "organism"]

    assembly = AssemblySerializer(read_only=True, many=False)
    organism = OrganismSerializer(many=False, read_only=True)
    datasets = serializers.HyperlinkedRelatedField(
        view_name='ensembl_metadata:dataset-detail',
        lookup_field='dataset_uuid',
        many=True, read_only=True)
    releases = ReleaseSerializer(many=True, read_only=True)
