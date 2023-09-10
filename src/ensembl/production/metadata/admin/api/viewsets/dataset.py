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
import uuid
from builtins import super
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ensembl.production.metadata.admin.api.serializers import DatasetSerializer
from ensembl.production.metadata.admin.models import Dataset, DatasetType, DatasetSource, DatasetAttribute, Attribute
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ensembl.production.metadata.admin.models import Genome

# @method_decorator(csrf_exempt, name='update')
class DatasetViewSet(viewsets.ModelViewSet):
    lookup_field = 'dataset_uuid'
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    # def get_permissions(self):
    #     if self.action in ['create', 'update', 'delete']:
    #         self.permission_classes = [AllowAny, ]
    #     return super(DatasetViewSet, self).get_permissions()

    def get_queryset(self):
        # Filters for queryset fields
        self.permission_classes = [AllowAny, ]
        queryset = Dataset.objects.all()
        topic = self.request.query_params.get('topic')
        released = self.request.query_params.get('released')
        unreleased = self.request.query_params.get('unreleased')
        if topic:
            queryset = queryset.filter(dataset_type__topic=topic)
        if released is not None:
            release_filter = Q(genome_datasets__release_id__isnull=False)
            queryset = queryset.filter(release_filter)
        if unreleased is not None:
            release_filter = Q(genome_datasets__release_id__isnull=False)
            queryset = queryset.exclude(release_filter)
        return queryset

    # #POST:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        User = get_user_model()
        self.permission_classes = [AllowAny, ]
        # Check if the user exists in the payload
        username = request.data.get('user', None)
        if not username or not User.objects.filter(username=username).exists():
            return Response({'detail': 'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if a dataset is already present and not released
        genome_uuid = request.data.get('genome_uuid')
        dataset_type_name = request.data.get('dataset_type')
        dataset_source_name = request.data.get('dataset_source', {}).get('name')
        existing_datasets = Dataset.objects.filter(
            dataset_type__name=dataset_type_name,
            dataset_source__name=dataset_source_name,
            genome_datasets__genome__genome_uuid=genome_uuid,
            genome_datasets__release__isnull=True,
        )
        if not Genome.objects.filter(genome_uuid=genome_uuid).exists():
            return Response({
                'error': 'No Genome found with the provided UUID.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if existing_datasets.exists():
            return Response({
                'error': 'Dataset with the provided genome_uuid, dataset_type.name and dataset_source.name '
                         'already exists. Please DELETE dataset and resubmit or PUT additional dataset_attributes.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    #PUT
    @method_decorator(csrf_exempt, name='dispatch')
    def update(self, request, dataset_uuid=None, *args, **kwargs):
        User = get_user_model()
        self.permission_classes = [AllowAny, ]
        username = request.data.get('user', None)
        if not username or not User.objects.filter(username=username).exists():
            return Response({'detail': 'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            dataset = Dataset.objects.get(dataset_uuid=dataset_uuid)
        except Dataset.DoesNotExist:
            return Response({'error': 'Please POST this data with type, genome, and dataset_source'},
                            status=status.HTTP_400_BAD_REQUEST)
        attrs_data = request.data.get('dataset_attribute', [])

        for attr_data in attrs_data:
            name = attr_data.get('name')
            value = attr_data.get('value')

            # Check if the attribute value already exists for the dataset
            if DatasetAttribute.objects.filter(dataset=dataset, attribute__name=name).exists():
                return Response(
                    {'error': f'Error, {name} is already populated. Please use the admin pages to modify it.'},
                    status=status.HTTP_400_BAD_REQUEST)

            # If not, update or create the dataset attribute
            attribute, created = Attribute.objects.get_or_create(
                name=name,
                defaults={
                    'label': name,
                    'description': name,
                    'type': "string"
                }
                )
            DatasetAttribute.objects.update_or_create(
                dataset=dataset,
                attribute=attribute,
                defaults={'value': value}
            )

        serializer = self.get_serializer(dataset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE:
    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [AllowAny, ]
        try:
            instance = self.get_object()
        except Dataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                dataset_source = instance.dataset_source
                if DatasetSource.objects.filter(name=dataset_source.name).count() == 1:
                    dataset_source.delete()
                else:
                    instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError:
            return Response({'error': 'Released data cannot be deleted'}, status=status.HTTP_400_BAD_REQUEST)
