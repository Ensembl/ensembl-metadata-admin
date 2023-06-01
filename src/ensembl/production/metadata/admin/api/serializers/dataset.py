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

from ensembl.production.metadata.admin.models import Dataset, Attribute, DatasetAttribute, DatasetSource, DatasetType

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['name', 'label']


class DatasetAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetAttribute
        fields = ['name', 'value']

    name = serializers.StringRelatedField(many=False, read_only=True, source='attribute')

class DatasetSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetSource
        fields = ['name','type']

class DatasetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetType
        fields = ['name','topic']

class DatasetSerializer(serializers.ModelSerializer):

    attributes = DatasetAttributeSerializer(many=True)
    genome_datasets = serializers.SerializerMethodField()
    dataset_source = DatasetSourceSerializer()
    dataset_type = DatasetTypeSerializer()

    class Meta:
        model = Dataset
        fields = ["dataset_uuid", "genome_datasets", "name", "label", "attributes","dataset_source","dataset_type"]

    def get_genome_datasets(self, obj):
        genome_datasets = obj.genome_datasets.all()
        serialized_data = []

        for genome_dataset in genome_datasets:
            genome = genome_dataset.genome
            release = genome_dataset.release if hasattr(genome_dataset, 'release') else None

            serialized_data.append({
                'is_current': genome_dataset.is_current,
                'genome_uuid': genome.genome_uuid,
                'release_version': release.version if release else None
            })
        return serialized_data

