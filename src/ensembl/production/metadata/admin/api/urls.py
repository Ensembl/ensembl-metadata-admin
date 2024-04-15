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

from django.urls import include, path
from rest_framework import routers

from ensembl.production.metadata.admin.api.viewsets import GenomeViewSet, UserViewSet, DatasetViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'genomes', GenomeViewSet)
router.register(r'datasets', DatasetViewSet)

urlpatterns = [
    path(f'', include((router.urls, 'ensembl_metadata'))),
    path(f'api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]