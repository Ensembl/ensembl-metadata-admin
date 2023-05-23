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

from ensembl.production.metadata.admin.models import Dataset, Attribute, DatasetAttribute

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
    class Meta:
        model = Dataset
        fields = ["dataset_uuid", "name", "label", "attributes"]

    attributes = DatasetAttributeSerializer(many=True)

