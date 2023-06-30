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


from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    path('api/metadata/', include('ensembl.production.metadata.admin.api.urls')),
    path('', admin.site.urls),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            template_name='../../templates/swagger-ui.html',
            url_name='schema',
        ),
        name='swagger-ui',
    )
]

