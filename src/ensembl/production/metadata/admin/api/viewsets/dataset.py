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
from rest_framework import viewsets, status
from ensembl.production.metadata.admin.api.serializers import DatasetSerializer
from ensembl.production.metadata.admin.models import Dataset
from django.db.models import Q
from rest_framework.response import Response
class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    lookup_field = 'dataset_uuid'
    def get_queryset(self):
        #Filters for queryset fields
        queryset = Dataset.objects.all()
        type = self.request.query_params.get('type')    #Don't know what this is?
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

#
# #POST:
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#
# #PUT
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)
#
# #DELETE
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)
