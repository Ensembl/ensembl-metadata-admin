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
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ensembl.production.metadata.admin.api.serializers import DatasetSerializer
from ensembl.production.metadata.admin.models import Dataset, DatasetSource, DatasetAttribute, Attribute
from ensembl.production.metadata.admin.models import Genome


class DatasetViewSet(viewsets.ModelViewSet):
    lookup_field = 'dataset_uuid'
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [AllowAny, ]

    @csrf_exempt
    def get_queryset(self):
        queryset = super().get_queryset()
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

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        User = get_user_model()
        self.permission_classes = [AllowAny, ]
        username = request.data.get('user', None)
        if not username or not User.objects.filter(username=username).exists():
            return Response({'detail': 'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)

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

    # PUT
    @csrf_exempt
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

    @csrf_exempt
    def perform_destroy(self, instance):
        with transaction.atomic():
            dataset_source = instance.dataset_source
            if Dataset.objects.filter(dataset_source_id=dataset_source.dataset_source_id).count() == 1:
                # delete datasource if now orphan
                dataset_source.delete()
            super().perform_destroy(instance)
