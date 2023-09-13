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
from django.core.exceptions import ObjectDoesNotExist


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['name', 'label']


class DatasetAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetAttribute
        fields = ['name', 'value']

    name = serializers.CharField(source='attribute.name')


class DatasetSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetSource
        fields = ['name', 'type']

    def validate(self, data):
        name = data.get('name')
        type_ = data.get('type')

        try:
            existing_source = DatasetSource.objects.get(name=name)
            if existing_source.type != type_:
                raise serializers.ValidationError({
                    "type": "Type mismatch for existing dataset source with the same name."
                })
        except DatasetSource.DoesNotExist:
            pass
        return data


class DatasetSerializer(serializers.ModelSerializer):
    dataset_attribute = DatasetAttributeSerializer(many=True, required=False)
    genome_uuid = serializers.UUIDField(write_only=True)
    genome_datasets = serializers.SerializerMethodField()
    dataset_source = DatasetSourceSerializer()
    dataset_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=DatasetType.objects.all()
    )

    class Meta:
        model = Dataset
        fields = ["dataset_uuid", "genome_datasets", "name", "label", "dataset_attribute", "dataset_source",
                  "dataset_type",
                  'genome_uuid']

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
        dataset_source_data = validated_data.pop('dataset_source', {})
        dataset_source_name = dataset_source_data.get('name')
        dataset_source_type = dataset_source_data.get('type')

        # Ensure that the data is committed in a single transaction
        with transaction.atomic():
            genome_uuid = validated_data.pop('genome_uuid')
            genome = Genome.objects.get(genome_uuid=genome_uuid)

            try:
                dataset_source = DatasetSource.objects.get(name=dataset_source_name)
                if dataset_source.type != dataset_source_type:
                    raise serializers.ValidationError({
                        "dataset_source": {
                            "name": ["dataset source with this name already exists with a different type."]
                        }
                    })
            except DatasetSource.DoesNotExist:
                try:
                    dataset_source = DatasetSource.objects.create(name=dataset_source_name, type=dataset_source_type)
                except Exception as e:
                    raise serializers.ValidationError({"dataset_source": str(e)})
            dataset_attributes_data = validated_data.pop('dataset_attribute', [])
            validated_data['dataset_source'] = dataset_source
            new_dataset = Dataset.objects.create(**validated_data)
            GenomeDataset.objects.create(genome=genome, dataset=new_dataset)
            for attr_data in dataset_attributes_data:
                attr_value = attr_data.get('value')
                attr_name = attr_data['attribute']['name']
                if not attr_name:
                    raise serializers.ValidationError("Attribute identifier name is required.")
                attribute, created = Attribute.objects.get_or_create(
                    name=attr_name,
                    defaults={
                        'label': attr_name,
                        'description': attr_name,
                        'type': "string"
                    }
                )
                DatasetAttribute.objects.create(dataset=new_dataset, attribute=attribute, value=attr_value)

        return new_dataset
