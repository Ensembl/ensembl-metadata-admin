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
from django.db import transaction
from ensembl.production.metadata.admin.models import Dataset, Attribute, DatasetAttribute, DatasetSource, DatasetType, \
    Genome, GenomeDataset
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['name', 'label']


class DatasetAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetAttribute
        fields = ['name', 'value']

    name = serializers.StringRelatedField(many=False, read_only=True, source='attribute')

class DatasetSerializer(serializers.ModelSerializer):
    attributes = DatasetAttributeSerializer(many=True,required=False)
    genome_uuid = serializers.UUIDField(write_only=True)
    genome_datasets = serializers.SerializerMethodField()
    dataset_source = serializers.SlugRelatedField(
        slug_field='name',
        queryset=DatasetSource.objects.all()
    )
    dataset_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=DatasetType.objects.all()
    )
    class Meta:
        model = Dataset
        fields = ["dataset_uuid", "genome_datasets", "name", "label", "attributes", "dataset_source", "dataset_type", 'genome_uuid']

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

    def create(self, validated_data):

        # Ensure that it is the data is commited in a single transaction
        with transaction.atomic():
            genome_uuid = validated_data.pop('genome_uuid')
            genome = Genome.objects.get(genome_uuid=genome_uuid)

            dataset_attributes_data = validated_data.get('dataset_attribute',[])


            # Create Dataset
            new_dataset = Dataset.objects.create(**validated_data)
            # Link new dataset to the genome
            GenomeDataset.objects.create(genome=genome, dataset=new_dataset)
            # Create DatasetAttributes if provided
            for attr_data in dataset_attributes_data:
                attr_value = attr_data.get('value')
                attr_name = attr_data.get('name')
                attr_id = attr_data.get('attribute_id')

                try:
                    if attr_name:
                        attribute = Attribute.objects.get(name=attr_name)
                    elif attr_id:
                        attribute = Attribute.objects.get(attribute_id=attr_id)
                    else:
                        raise serializers.ValidationError("Attribute identifier (name or attribute_id) is required.")
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Attribute not found.")

                DatasetAttribute.objects.create(dataset=new_dataset, attribute=attribute, value=attr_value)

        return new_dataset
