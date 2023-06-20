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

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from ensembl.production.metadata.admin.api.serializers import DatasetSerializer, GenomeSerializer
from ensembl.production.metadata.admin.models import Dataset, DatasetType, DatasetSource, GenomeDataset, \
    DatasetAttribute
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ensembl.production.metadata.admin.models import Genome
from uuid import UUID


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    lookup_field = 'dataset_uuid'

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny, ]
        return super(DatasetViewSet, self).get_permissions()

    def get_queryset(self):
        # Filters for queryset fields
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

        # Check if the user exists in the payload
        username = request.data.get('user', None)
        if not username or not User.objects.filter(username=username).exists():
            return Response({'detail': 'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)

        # Require Genome_uuid, dataset_type_name, dataset_source
        genome_uuid = request.data.get('genome_uuid')
        dataset_type_name = request.data.get('dataset_type')
        dataset_source_name = request.data.get('dataset_source')

        if not all([genome_uuid, dataset_type_name, dataset_source_name]):
            return Response({'error': 'Required fields not provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if  Genome_uuid, dataset_type_name, dataset_source are present in the database:
        if not DatasetSource.objects.filter(name=dataset_source_name).exists():
            return Response({'error': 'The provided dataset_source_name does not exist in the database'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            Genome.objects.get(genome_uuid=uuid.UUID(genome_uuid))
        except Genome.DoesNotExist:
            return Response({'error': 'The provided genome_uuid does not exist in the database'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not DatasetType.objects.filter(name=dataset_type_name).exists():
            return Response({'error': 'The provided dataset_type_name does not exist in the database'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a dateset is already present and not release:
        existing_datasets = Dataset.objects.filter(
            dataset_type__name=dataset_type_name,
            dataset_source__name=dataset_source_name,
            genome_datasets__genome__genome_uuid=genome_uuid,
            genome_datasets__release__isnull=True,
        )
        if existing_datasets.exists():
            return Response({
                'error': 'Dataset with the provided genome_uuid, dataset_type.name and dataset_source.name '
                         'already exists and is not attached to a release. Please use PUT to update instead of POST.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # DELETE:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)